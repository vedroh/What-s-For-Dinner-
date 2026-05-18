from flask import Flask, render_template, request, session, redirect, url_for, abort, flash, jsonify
import sqlite3
import datetime
import json
import os
from werkzeug.utils import secure_filename
from receipt_scanner import scan_receipt

app = Flask(__name__)
app.secret_key = 'hhdsvbdjcn6r6283br30000919889384b'


# НАСТРОЙКА ЗАГРУЗКИ ФАЙЛОВ
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ПОЛЬЗОВАТЕЛИ
USERS = {
    'admin': {'password': '12345', 'name': 'Admin'},
    'user': {'password': '1234', 'name': 'User'}
}


# ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ
def get_db():
    conn = sqlite3.connect('recipes.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    return render_template('index.html', title='Home')


@app.route('/login')
def login_page():
    return render_template('login.html', title='Login')


# POST - ОБРАБОТКА ДАННЫХ
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username in USERS and USERS[username]['password'] == password:
        # УСПЕШНЫЙ ВХОД
        session['username'] = username
        session['user_name'] = USERS[username]['name']
        flash('Login successful!', 'success')
        return redirect(url_for('index'))
    else:
        # НЕУДАЧНЫЙ ВХОД
        flash('Invalid login or password', 'danger')
        return redirect(url_for('login_page'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    # ПРОВЕРКА АВТОРИЗАЦИИ
    if 'username' not in session:
        flash('Please log in first', 'warning')
        return redirect(url_for('login_page'))
    
    # СТАТИСТИКА ИЗ БД
    username = session['username']
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT action, COUNT(*) FROM user_actions WHERE username = ? GROUP BY action", (username,))
    actions = cursor.fetchall()
    
    # СТАТИСТИКА
    stats = {'favorite': 0, 'will_cook': 0, 'cooked': 0, 'hide': 0}
    for action in actions:
        if action['action'] == 'favorite':
            stats['favorite'] = action[1]
        elif action['action'] == 'will_cook':
            stats['will_cook'] = action[1]
        elif action['action'] == 'cooked':
            stats['cooked'] = action[1]
    
    conn.close()
    return render_template('profile.html', title='Profile', stats=stats)


@app.route('/recipes/<category>')
def recipes(category):
    #  РЕЦЕПТЫ ИЗ БД ПО КАТЕГОРИИ
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipes WHERE category = ?", (category,))
    recipes_list = cursor.fetchall()
    
    # ДЕЙСТВИЯ ПОЛЬЗОВАТЕЛЯ ПО КАТЕГОРИЯМ
    user_actions = {}
    if 'username' in session:
        username = session['username']
        recipe_ids = [r['id'] for r in recipes_list]
        if recipe_ids:
            placeholders = ','.join('?' * len(recipe_ids))
            cursor.execute(f"SELECT recipe_id, action FROM user_actions WHERE username = ? AND recipe_id IN ({placeholders})", 
                          (username,) + tuple(recipe_ids))
            for row in cursor.fetchall():
                user_actions[row['recipe_id']] = row['action']
    
    conn.close()
    
    category_names = {'first': 'First Dishes', 'second': 'Main Dishes', 'appetizers': 'Appetizers', 'desserts': 'Desserts'}
    return render_template('recipes.html', title=category_names.get(category, 'Recipes'), 
                         category=category, recipes=recipes_list, user_actions=user_actions)

# ДЕТАЛИ РЕЦЕПТА
@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
    recipe = cursor.fetchone()
    
    user_action = None
    if 'username' in session:
        cursor.execute("SELECT action FROM user_actions WHERE username = ? AND recipe_id = ?", 
                      (session['username'], recipe_id))
        row = cursor.fetchone()
        if row:
            user_action = row['action']
    
    conn.close()
    
    if recipe is None:
        abort(404)
    
    return render_template('recipe_detail.html', title=recipe['name'], 
                         recipe=recipe, user_action=user_action)


# ОБРАБОТКА КНОПОК
@app.route('/action/<int:recipe_id>/<action>')
def user_action(recipe_id, action):
    if 'username' not in session:
        return jsonify({'error': 'Please log in'}), 401
    
    username = session['username']
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM user_actions WHERE username = ? AND recipe_id = ?", (username, recipe_id))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("UPDATE user_actions SET action = ?, date = ? WHERE username = ? AND recipe_id = ?",
                      (action, date, username, recipe_id))
    else:
        cursor.execute("INSERT INTO user_actions (username, recipe_id, action, date) VALUES (?, ?, ?, ?)",
                      (username, recipe_id, action, date))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'action': action})

# API сканирования чека
@app.route('/api/scan_receipt', methods=['POST'])
def api_scan_receipt():
    
    if 'receipt' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['receipt']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Сохраняем файл
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        products = scan_receipt(filepath)
        
        # Ищем рецепты по продуктам
        if products:
            search_ingredients = [p.lower() for p in products]
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recipes")
            all_recipes = cursor.fetchall()
            conn.close()
            
            results = []
            for recipe in all_recipes:
                recipe_ingredients = [i.strip().lower() for i in recipe['ingredients'].split(',')]
                matches = sum(1 for ing in search_ingredients if any(ing in ri for ri in recipe_ingredients))
                
                if matches > 0:
                    match_percentage = (matches / len(search_ingredients)) * 100
                    recipe_dict = dict(recipe)
                    recipe_dict['match_percentage'] = round(match_percentage, 1)
                    results.append(recipe_dict)
            
            results.sort(key=lambda x: x['match_percentage'], reverse=True)
            
            return jsonify({
                'success': True,
                'products': products,
                'recipes': results[:10]
            })
        else:
            return jsonify({
                'success': True,
                'products': [],
                'recipes': [],
                'message': 'No products recognized'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Удаляем временный файл
        if os.path.exists(filepath):
            os.remove(filepath)


@app.route('/scan')
def scan():
    return render_template('scan.html', title='Scan Receipt')


@app.route('/search')
def search():
    return render_template('search.html', title='Search Recipes')


@app.route('/api/search_recipes')
def api_search_recipes():
    ingredients = request.args.get('ingredients', '')
    
    if not ingredients:
        return jsonify([])
    
    search_ingredients = [i.strip().lower() for i in ingredients.split(',')]
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipes")
    all_recipes = cursor.fetchall()
    conn.close()
    
    # ДЛЯ КАЖДОГО РЕЦЕПТА СЧИТАЕМ СОВПАДЕНИЯ
    results = []
    for recipe in all_recipes:
        recipe_ingredients = [i.strip().lower() for i in recipe['ingredients'].split(',')]
        matches = sum(1 for ing in search_ingredients if any(ing in ri for ri in recipe_ingredients))
        
        if matches > 0:
            match_percentage = (matches / len(search_ingredients)) * 100
            recipe_dict = dict(recipe)
            recipe_dict['match_percentage'] = round(match_percentage, 1)
            results.append(recipe_dict)
    
    # СОРТИРУЕМ ПО ПРОЦЕНТУ СОВПАДЕНИЯ
    results.sort(key=lambda x: x['match_percentage'], reverse=True)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (recipe['name'], recipe['category'], recipe['ingredients'], 
                      recipe['instructions'], recipe['cooking_time'], recipe['servings'],
                      recipe['source'], recipe['image_url'], recipe['rating'], recipe['description']))
        print("Database populated with recipes!")
    
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect('recipes.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/login')
def login_page():
    return render_template('login.html', title='Login')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username in USERS and USERS[username]['password'] == password:
        session['username'] = username
        session['user_name'] = USERS[username]['name']
        flash('Login successful!', 'success')
        return redirect(url_for('index'))
    else:
        flash('Invalid login or password', 'danger')
        return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'username' not in session:
        flash('Please log in first', 'warning')
        return redirect(url_for('login_page'))
    
    username = session['username']
    conn = get_db()
    cursor = conn.cursor()
    
    # Статистика действий пользователя
    cursor.execute("SELECT action, COUNT(*) FROM user_actions WHERE username = ? GROUP BY action", (username,))
    actions = cursor.fetchall()
    
    stats = {
        'favorite': 0,
        'will_cook': 0,
        'cooked': 0,
        'hide': 0
    }
    
    for action in actions:
        if action['action'] == 'favorite':
            stats['favorite'] = action[1]
        elif action['action'] == 'will_cook':
            stats['will_cook'] = action[1]
        elif action['action'] == 'cooked':
            stats['cooked'] = action[1]
        elif action['action'] == 'hide':
            stats['hide'] = action[1]
    
    conn.close()
    
    return render_template('profile.html', title='Profile', stats=stats)

@app.route('/recipes/<category>')
def recipes(category):
    conn = get_db()
    cursor = conn.cursor()
    
    # Получаем все рецепты категории
    cursor.execute("SELECT * FROM recipes WHERE category = ?", (category,))
    recipes_list = cursor.fetchall()
    
    # Получаем действия пользователя ТОЛЬКО если он залогинен
    user_actions = {}
    if 'username' in session:
        username = session['username']
        recipe_ids = [r['id'] for r in recipes_list]
        if recipe_ids:
            placeholders = ','.join('?' * len(recipe_ids))
            cursor.execute(f"SELECT recipe_id, action FROM user_actions WHERE username = ? AND recipe_id IN ({placeholders})", 
                          (username,) + tuple(recipe_ids))
            for row in cursor.fetchall():
                user_actions[row['recipe_id']] = row['action']
    
    conn.close()
    
    category_names = {
        'first': 'First Dishes',
        'second': 'Main Dishes',
        'appetizers': 'Appetizers',
        'desserts': 'Desserts'
    }
    
    # Всегда передаем user_actions (даже если пустой словарь)
    return render_template('recipes.html', 
                         title=category_names.get(category, 'Recipes'), 
                         category=category, 
                         recipes=recipes_list, 
                         user_actions=user_actions)

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
    recipe = cursor.fetchone()
    
    cursor.execute("SELECT * FROM reviews WHERE recipe_id = ? ORDER BY date DESC", (recipe_id,))
    reviews = cursor.fetchall()
    
    # Получаем действие пользователя ТОЛЬКО если он залогинен
    user_action = None
    if 'username' in session:
        cursor.execute("SELECT action FROM user_actions WHERE username = ? AND recipe_id = ?", 
                      (session['username'], recipe_id))
        row = cursor.fetchone()
        if row:
            user_action = row['action']
    
    conn.close()
    
    if recipe is None:
        abort(404)
    
    return render_template('recipe_detail.html', 
                         title=recipe['name'], 
                         recipe=recipe, 
                         reviews=reviews, 
                         user_action=user_action)

@app.route('/add_review/<int:recipe_id>', methods=['POST'])
def add_review(recipe_id):
    if 'username' not in session:
        flash('Please log in to leave a review', 'warning')
        return redirect(url_for('login_page'))
    
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    username = session['username']
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO reviews (recipe_id, username, rating, comment, date)
                     VALUES (?, ?, ?, ?, ?)''',
                  (recipe_id, username, rating, comment, date))
    conn.commit()
    conn.close()
    
    flash('Review added!', 'success')
    return redirect(url_for('recipe_detail', recipe_id=recipe_id))

@app.route('/action/<int:recipe_id>/<action>')
def user_action(recipe_id, action):
    if 'username' not in session:
        return jsonify({'error': 'Please log in'}), 401
    
    username = session['username']
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже действие
    cursor.execute("SELECT id FROM user_actions WHERE username = ? AND recipe_id = ?", (username, recipe_id))
    existing = cursor.fetchone()
    
    if existing:
        # Обновляем существующее действие
        cursor.execute("UPDATE user_actions SET action = ?, date = ? WHERE username = ? AND recipe_id = ?",
                      (action, date, username, recipe_id))
    else:
        # Добавляем новое действие
        cursor.execute("INSERT INTO user_actions (username, recipe_id, action, date) VALUES (?, ?, ?, ?)",
                      (username, recipe_id, action, date))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'action': action})

@app.route('/scan')
def scan_receipt():
    return render_template('scan.html', title='Scan Receipt')

@app.route('/search')
def search():
    return render_template('search.html', title='Search Recipes')

@app.route('/api/search_recipes')
def api_search_recipes():
    ingredients = request.args.get('ingredients', '')
    
    if not ingredients:
        return jsonify([])
    
    search_ingredients = [i.strip().lower() for i in ingredients.split(',')]
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipes")
    all_recipes = cursor.fetchall()
    conn.close()
    
    results = []
    for recipe in all_recipes:
        recipe_ingredients = [i.strip().lower() for i in recipe['ingredients'].split(',')]
        
        matches = sum(1 for ing in search_ingredients if any(ing in ri for ri in recipe_ingredients))
        if matches > 0:
            match_percentage = (matches / len(search_ingredients)) * 100
            recipe_dict = dict(recipe)
            recipe_dict['match_percentage'] = round(match_percentage, 1)
            results.append(recipe_dict)
    
    results.sort(key=lambda x: x['match_percentage'], reverse=True)
    return jsonify(results)



if __name__ == '__main__':
    app.run(debug=True)

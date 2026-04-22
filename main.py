from flask import Flask, render_template, request, session, redirect, url_for, abort, flash, jsonify
import sqlite3
import datetime
import json

app = Flask(__name__)
app.secret_key = 'hhdsvbdjcn6r6283br30000919889384b'

USERS = {
    'admin': {'password': '12345', 'name': 'Admin'},
    'user': {'password': '1234', 'name': 'User'}
}

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    
    # Таблица рецептов
    c.execute('''CREATE TABLE IF NOT EXISTS recipes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  category TEXT NOT NULL,
                  ingredients TEXT NOT NULL,
                  instructions TEXT NOT NULL,
                  cooking_time INTEGER,
                  servings INTEGER,
                  source TEXT,
                  image_url TEXT,
                  rating REAL,
                  description TEXT)''')
    
    # Таблица отзывов
    c.execute('''CREATE TABLE IF NOT EXISTS reviews
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  recipe_id INTEGER,
                  username TEXT,
                  rating INTEGER,
                  comment TEXT,
                  date TEXT,
                  FOREIGN KEY (recipe_id) REFERENCES recipes (id))''')
    
    # Таблица действий пользователя
    c.execute('''CREATE TABLE IF NOT EXISTS user_actions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  recipe_id INTEGER,
                  action TEXT,
                  date TEXT,
                  UNIQUE(username, recipe_id),
                  FOREIGN KEY (recipe_id) REFERENCES recipes (id))''')
    
    # Проверяем, есть ли данные в таблице рецептов
    c.execute("SELECT COUNT(*) FROM recipes")
    count = c.fetchone()[0]
    
    if count == 0:
        from recipes_data import recipes_dataset
        for recipe in recipes_dataset:
            c.execute('''INSERT INTO recipes 
                        (name, category, ingredients, instructions, cooking_time, servings, source, image_url, rating, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
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
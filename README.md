# 🍽️ What's For Dinner?

[![Flask](https://img.shields.io/badge/Flask-2.3-black)](https://flask.palletsprojects.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)](https://getbootstrap.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-blue)](https://sqlite.org/)

**AI-powered recipe finder that helps you cook delicious meals using ingredients you already have!**

---

## 📖 About The Project

**What's For Dinner?** is a full-stack web application that solves the eternal question: "What should I cook today?"

Simply scan your grocery receipt or type in the ingredients you have at home, and our smart search engine will find the best matching recipes from our curated database. Save your favorite recipes, track what you've cooked, and build your personal cookbook!

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Smart Search** | Find recipes by ingredients - enter what you have, get what you can cook |
| 📷 **Receipt Scanner** | Upload a photo of your grocery receipt (AI-ready) |
| ❤️ **Recipe Actions** | Mark recipes as Favorite, Will Cook, or Already Cooked |
| 👤 **User Profile** | Track your cooking statistics and saved recipes |
| ⭐ **Reviews & Ratings** | Leave comments and rate recipes you've tried |
| 📱 **Responsive Design** | Works perfectly on desktop, tablet, and mobile |

### 🗂️ Recipe Categories

- 🍲 **First Dishes** - Soups, borscht, fish soup
- 🍛 **Main Dishes** - Plov, pasta, meat dishes
- 🥗 **Appetizers** - Salads, starters, cold dishes
- 🍰 **Desserts** - Cakes, cheesecakes, sweet treats

---

## 🛠️ Built With

### Backend
- **Flask** - Lightweight WSGI web framework
- **SQLite3** - Embedded database for recipes and user data
- **Jinja2** - Template engine for dynamic HTML

### Frontend
- **Bootstrap 5** - Responsive CSS framework
- **Font Awesome 6** - Icon library
- **jQuery** - AJAX requests for interactive features

---

## 📂 Project Structure

```
whats-for-dinner/
├── main.py                 # Flask application with routes
├── recipes_data.py         # Recipe dataset (8 curated recipes)
├── recipes.db              # SQLite database (auto-generated)
├── static/
│   ├── css/
│   │   ├── bootstrap.min.css
│   │   └── style.css
│   ├── js/
│   │   ├── bootstrap.min.js
│   │   └── script.js
│   └── images/
│       └── favicon.png
└── templates/
    ├── base.html
    ├── index.html
    ├── recipes.html
    ├── recipe_detail.html
    ├── search.html
    ├── scan.html
    ├── profile.html
    └── login.html
```

---

## 🔧 Installation

### Prerequisites
- Python 3.8 or higher

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/whats-for-dinner.git
cd whats-for-dinner
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Flask**
```bash
pip install flask
```

4. **Run the application**
```bash
python main.py
```

5. **Open your browser**
```
http://127.0.0.1:5000
```

### Default Login Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | 12345 | Administrator |
| user | 1234 | Regular user |

---

## 🎯 How It Works

### 1. Search by Ingredients
Enter ingredients separated by commas (e.g., "chicken, potatoes, onion"). The app compares your ingredients against recipe databases and returns matches sorted by relevance.

### 2. Receipt Scanner (Demo)
Upload a photo of your grocery receipt. The app currently uses demo data to show matching recipes (OCR integration coming soon).

### 3. Recipe Actions
When logged in, you can mark recipes with:
- ❤️ **Favorite** - Save for later
- ⏰ **Will Cook** - Plan to make soon
- ✅ **Cooked** - Track what you've made



## 🎨 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search_recipes?ingredients=...` | GET | Search recipes by ingredients |
| `/action/<recipe_id>/<action>` | GET | Save user action |
| `/add_review/<recipe_id>` | POST | Add a review to a recipe |


---

## 🤝 Contributing

Contributions are welcome! Feel free to:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📧 Contact

**Team Members:**
- @vedroh
- @eva_chernaya
- @Khorets_Ekaterina

**Project Link:** [https://github.com/yourusername/whats-for-dinner](https://github.com/yourusername/whats-for-dinner)

---

## 📄 License

Distributed under the MIT License.

---

## ⭐ Show Your Support

If this project helped you, please give it a ⭐ on GitHub!

---

*Made with ❤️ for the love of cooking and coding*

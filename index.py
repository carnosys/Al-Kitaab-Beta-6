import os
import json
from flask import Flask, render_template, redirect, url_for, request, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
# Secret key for session management
app.secret_key = 'session1'

# MySQL Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Funandplay123!',
    'database': 'al_kitab'
}

# Load Quran surahs from the JSON file dynamically
surahs_path = os.path.join(app.root_path, 'quran_surahs.json')
with open(surahs_path, 'r', encoding='utf-8') as f:
    surahs = json.load(f)

# MySQL connection helper
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None

# Route for home page (only accessible if logged in)
@app.route('/')
def home_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    
    # Check if user is admin
    conn = get_db_connection()# idhr se start hoga
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT role FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and user['role'] == 'admin':
            return redirect(url_for('admin_portal'))#idhr pe end
    
    return render_template('index.html', surahs=surahs, username=username)

# Login and Signup
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form['action']
        username = request.form['username']
        email = request.form.get('email')
        password = request.form['password']

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            if action == 'signin':
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
                if user and user['password'] == password:
                    session['username'] = username
                    # Check if user is admin
                    if user.get('role') == 'admin':#idhr se start hoga
                        return redirect(url_for('admin_portal'))#idhr pe end
                    return redirect(url_for('home_page'))
                else:
                    return render_template('login.html', error="Invalid username or password")
            elif action == 'signup':
                cursor.execute(
                    "SELECT * FROM users WHERE username = %s OR user_email = %s", (username, email)
                )
                existing = cursor.fetchone()
                if existing:
                    return render_template('login.html', error="Username or Email already exists")
                cursor.execute(
                    "INSERT INTO users (username, user_email, password) VALUES (%s, %s, %s)",
                    (username, email, password)
                )
                conn.commit()
                session['username'] = username
                return redirect(url_for('user_info'))
            cursor.close()
            conn.close()
        else:
            return render_template('login.html', error="Database connection error")
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# User info setup
@app.route('/user-info', methods=['GET', 'POST'])
def user_info():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('user-info.html')

# Additional static routes
@app.route('/progress-and-analytics')
def progress():
    return render_template('progressAndAnalysitcs.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/profile-settings')
def profile_settings():
    return render_template('profileSettings.html')

# Admin portal route
@app.route('/admin')
def admin_portal():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    users = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id, username, user_email, role, status FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
    
    return render_template('adminBase.html', users=users, username=session['username'])

# Add routes for user management
@app.route('/admin/update_user', methods=['POST'])
def update_user():
    if 'username' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401
        
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    email = request.form.get('email')
    role = request.form.get('role')
    status = request.form.get('status')
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET username = %s, user_email = %s, role = %s, status = %s 
                WHERE user_id = %s
            """, (name, email, role, status, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            return {'success': True, 'message': 'User updated successfully'}
        except Error as e:
            return {'success': False, 'message': str(e)}, 500
    return {'success': False, 'message': 'Database error'}, 500

@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401
        
    user_id = request.form.get('user_id')
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return {'success': True, 'message': 'User deleted successfully'}
        except Error as e:
            return {'success': False, 'message': str(e)}, 500
    return {'success': False, 'message': 'Database error'}, 500

# Import and register the surah page blueprint
from surah_page import surah_page_bp
app.register_blueprint(surah_page_bp)

if __name__ == '__main__':
    app.run(debug=True)


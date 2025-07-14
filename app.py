# from flask import Flask, render_template, request, redirect, url_for, session, flash
# from werkzeug.security import generate_password_hash ,check_password_hash 
# import mysql.connector



# app = Flask(__name__)
# app.secret_key = 'secret_key'
# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="",
#     database="school_db"
# )
# @app.route('/')
# def hallo_world():

#     return render_template('home.html')
# @app.route('/login')
# def login():
#     return render_template('login.html')  
# @app.route('/login', methods=['GET', 'POST'])
# def do_login():
#     email = request.form.get('username')
#     password = request.form.get('password')
    
#     cursor = db.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM users WHERE email = %s AND status = 'active'", (email,))
#     user = cursor.fetchone()
#     result =check_password_hash(user['password'], password)
#     paw= user['password']
#     if user and check_password_hash(user['password'], password):
#         session['user_id'] = user['id']
#         session['username'] = user['name']
#         session['role'] = user['role']

#         if user['role'] == 'admin':
#             return redirect(url_for('admin_home'))
#         elif user['role'] == 'teacher':
#             return redirect(url_for('teacher_home'))
#         elif user['role'] == 'parent':
#             return redirect(url_for('parent_home'))
#     else:
#         flash("Invalid credentials or inactive account ", "danger")
#         flash( user['password'] ,"danger")
#         return redirect(url_for('login'))
    
# @app.route('/register_teacher', methods=['GET', 'POST'])
# def register_teacher():
#     if session.get('role') != 'admin':
#         flash("Unauthorized access", "danger")
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         password = request.form['password']
#         assigned_class = request.form['assigned_class']

#         hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

#         cursor = db.cursor()

#         # Check if email already exists
#         cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
#         if cursor.fetchone():
#             flash("Email already exists!", "warning")
#             return redirect(url_for('register_teacher'))

#         # Insert into users table
#         cursor.execute("INSERT INTO users (name, email, password, role, status) VALUES (%s, %s, %s, %s, %s)",
#                        (name, email, hashed_password, 'teacher', 'pending'))
#         user_id = cursor.lastrowid  # Get ID of the new user

#         # Insert into teachers table
#         cursor.execute("INSERT INTO teachers (user_id, class_assigned) VALUES (%s, %s)", (user_id, assigned_class))

#         db.commit()
#         flash("Teacher registered successfully!", "success")
#         return redirect(url_for('admin_home'))

#     return render_template('register_teacher.html')

# @app.route('/admin')
# def admin_home():
#     if session.get('role') == 'admin':
#         return render_template('admin_home.html')
#     return redirect(url_for('login'))
# @app.route('/teacher')
# def teacher_home():
#     if session.get('role') == 'teacher':
#         return render_template('teacher_home.html')
#     return redirect(url_for('login'))
# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('login'))
# if __name__ == "__main__":
#     app.run(debug=True)
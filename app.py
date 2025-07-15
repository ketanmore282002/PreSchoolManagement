from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash ,check_password_hash 
import mysql.connector



app = Flask(__name__)
app.secret_key = 'secret_key'
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="school_db"
)
@app.route('/')
def hallo_world():

    return render_template('home.html')
@app.route('/login')
def login():
    return render_template('login.html')  
@app.route('/login', methods=['GET', 'POST'])
def do_login():
    email = request.form.get('username')
    password = request.form.get('password')
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s AND status = 'active'", (email,))
    user = cursor.fetchone()
    result =check_password_hash(user['password'], password)
    paw= user['password']
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['name']
        session['role'] = user['role']

        if user['role'] == 'admin':
            return redirect(url_for('admin_home'))
        elif user['role'] == 'teacher':
            return redirect(url_for('teacher_home'))
        elif user['role'] == 'parent':
            return redirect(url_for('parent_home'))
    else:
        flash("Invalid credentials or inactive account ", "danger")
        flash( user['password'] ,"danger")
        return redirect(url_for('login'))
    
@app.route('/register_teacher', methods=['GET', 'POST'])
def register_teacher():
    if session.get('role') != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        assigned_class = request.form['assigned_class']

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        cursor = db.cursor()

        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("Email already exists!", "warning")
            return redirect(url_for('register_teacher'))

        # Insert into users table
        cursor.execute("INSERT INTO users (name, email, password, role, status) VALUES (%s, %s, %s, %s, %s)",
                       (name, email, hashed_password, 'teacher', 'active'))
        user_id = cursor.lastrowid  # Get ID of the new user

        # Insert into teachers table
        cursor.execute("INSERT INTO teachers (user_id, class_assigned) VALUES (%s, %s)", (user_id, assigned_class))

        db.commit()
        flash("Teacher registered successfully!", "success")
        return redirect(url_for('admin_home'))

    return render_template('register_teacher.html')
@app.route('/teachers', methods=['GET', 'POST'])
def view_teachers():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)
    query = """
        SELECT users.id, users.name, users.email, users.status, teachers.class_assigned
        FROM users
        JOIN teachers ON users.id = teachers.user_id
        WHERE users.role = 'teacher'
    """
    cursor.execute(query)
    teachers = cursor.fetchall()
    cursor.close()

    return render_template('view_teachers.html', teachers=teachers)
# Edit teacher
@app.route('/edit_teacher/<int:id>', methods=['GET', 'POST'])
def edit_teacher(id):
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        class_assigned = request.form['assigned_class']
        
        cursor.execute("UPDATE users SET name=%s, email=%s WHERE id=%s", (name, email, id))
        cursor.execute("UPDATE teachers SET class_assigned=%s WHERE user_id=%s", (class_assigned, id))
        db.commit()
        cursor.close()
        flash("Teacher updated successfully", "success")
        return redirect(url_for('view_teachers'))

    cursor.execute("""
        SELECT users.name, users.email, teachers.class_assigned
        FROM users
        JOIN teachers ON users.id = teachers.user_id
        WHERE users.id = %s
    """, (id,))
    teacher = cursor.fetchone()
    cursor.close()

    return render_template('edit_teacher.html', teacher=teacher, id=id)
#  delet teacher
@app.route('/delete_teacher/<int:id>')
def delete_teacher(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM teachers WHERE user_id = %s", (id,))
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    db.commit()
    cursor.close()
    flash("Teacher deleted successfully", "info")
    return redirect(url_for('view_teachers'))
# Togel active /padding
@app.route('/toggle_teacher_status/<int:id>')
def toggle_teacher_status(id):
    cursor = db.cursor()
    cursor.execute("SELECT status FROM users WHERE id = %s", (id,))
    current_status = cursor.fetchone()[0]

    new_status = 'pending' if current_status == 'active' else 'active'
    cursor.execute("UPDATE users SET status = %s WHERE id = %s", (new_status, id))
    db.commit()
    cursor.close()
    flash(f"Status changed to {new_status}", "warning")
    return redirect(url_for('view_teachers'))

      # prarent registrarion
@app.route('/register_parent', methods=['GET', 'POST'])
def parent_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        cursor = db.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("Email already exists!", "warning")
            return redirect(url_for('parent_register'))

        cursor.execute(
            "INSERT INTO users (name, email, password, role, status) VALUES (%s, %s, %s, %s, %s)",
            (name, email, hashed_password, 'parent', 'pending')
        )
        db.commit()
        cursor.close()

        flash("Registration successful! Awaiting admin approval.", "info")
        return redirect(url_for('login'))

    return render_template('parent_register.html')

@app.route('/approve_parent/<int:id>')
def approve_parent(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    cursor = db.cursor()
    cursor.execute("UPDATE users SET status = 'active' WHERE id = %s AND role = 'parent'", (id,))
    db.commit()
    cursor.close()

    flash("Parent approved successfully", "success")
    return redirect(url_for('pending_parents'))

@app.route('/reject_parent/<int:id>')
def reject_parent(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s AND role = 'parent'", (id,))
    db.commit()
    cursor.close()

    flash("Parent request rejected", "danger")
    return redirect(url_for('pending_parents'))

# show parent list
@app.route('/pending_parents')
def pending_parents():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email FROM users WHERE role = 'parent' AND status = 'pending'")
    parents = cursor.fetchall()
    cursor.close()

    return render_template('pending_parents.html', parents=parents)


@app.route('/admin')
def admin_home():
    if session.get('role') == 'admin':
        return render_template('admin_home.html')
    return redirect(url_for('login'))
@app.route('/teacher')
def teacher_home():
    if session.get('role') == 'teacher':
        return render_template('teacher_home.html')
    return redirect(url_for('login'))
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
if __name__ == "__main__":
    app.run(debug=True)
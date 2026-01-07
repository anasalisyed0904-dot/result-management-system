from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'
DATABASE = 'results.db'

# Initialize database
if not os.path.exists(DATABASE):
    import database
    database.init_db()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Login route
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and user['password'] == password:  # In production, use proper password hashing
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get counts for dashboard
    student_count = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    result_count = conn.execute('SELECT COUNT(*) FROM results').fetchone()[0]
    
    # Get recent results
    recent_results = conn.execute('''
        SELECT r.*, s.name 
        FROM results r 
        JOIN students s ON r.student_id = s.student_id 
        ORDER BY r.id DESC LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         student_count=student_count,
                         result_count=result_count,
                         recent_results=recent_results)

# Add Student
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        student_class = request.form['class']
        email = request.form['email']
        phone = request.form['phone']
        
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO students (student_id, name, class, email, phone)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, name, student_class, email, phone))
            conn.commit()
            flash('Student added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Student ID already exists!', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('add_student'))
    
    return render_template('add_student.html')

# Add Result
@app.route('/add_result', methods=['GET', 'POST'])
def add_result():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        subject = request.form['subject']
        marks = int(request.form['marks'])
        max_marks = int(request.form['max_marks'])
        semester = request.form['semester']
        year = request.form['year']
        
        # Calculate grade
        percentage = (marks / max_marks) * 100
        if percentage >= 90:
            grade = 'A+'
        elif percentage >= 80:
            grade = 'A'
        elif percentage >= 70:
            grade = 'B'
        elif percentage >= 60:
            grade = 'C'
        elif percentage >= 50:
            grade = 'D'
        else:
            grade = 'F'
        
        conn.execute('''
            INSERT INTO results (student_id, subject, marks, max_marks, grade, semester, year)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, subject, marks, max_marks, grade, semester, year))
        conn.commit()
        
        flash('Result added successfully!', 'success')
        return redirect(url_for('add_result'))
    
    # Get students for dropdown
    students = conn.execute('SELECT student_id, name FROM students ORDER BY name').fetchall()
    conn.close()
    
    return render_template('add_result.html', students=students)

# View Results
@app.route('/view_results')
def view_results():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get filter parameters
    student_id = request.args.get('student_id', '')
    semester = request.args.get('semester', '')
    year = request.args.get('year', '')
    
    # Build query
    query = '''
        SELECT r.*, s.name, s.class 
        FROM results r 
        JOIN students s ON r.student_id = s.student_id 
        WHERE 1=1
    '''
    params = []
    
    if student_id:
        query += ' AND r.student_id = ?'
        params.append(student_id)
    
    if semester:
        query += ' AND r.semester = ?'
        params.append(semester)
    
    if year:
        query += ' AND r.year = ?'
        params.append(year)
    
    query += ' ORDER BY r.year DESC, r.semester, s.name'
    
    results = conn.execute(query, params).fetchall()
    
    # Get unique semesters and years for filters
    semesters = conn.execute('SELECT DISTINCT semester FROM results ORDER BY semester').fetchall()
    years = conn.execute('SELECT DISTINCT year FROM results ORDER BY year DESC').fetchall()
    students = conn.execute('SELECT student_id, name FROM students ORDER BY name').fetchall()
    
    conn.close()
    
    return render_template('view_results.html', 
                         results=results,
                         semesters=semesters,
                         years=years,
                         students=students,
                         filters={'student_id': student_id, 'semester': semester, 'year': year})

# Search Students
@app.route('/search_student')
def search_student():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    query = request.args.get('q', '')
    conn = get_db_connection()
    
    students = conn.execute('''
        SELECT student_id, name, class 
        FROM students 
        WHERE student_id LIKE ? OR name LIKE ? 
        LIMIT 10
    ''', (f'%{query}%', f'%{query}%')).fetchall()
    
    conn.close()
    
    return jsonify([dict(student) for student in students])

# Add this route after line 70 in app.py (after the login route)
@app.route('/admin/view_data')
def admin_view_data():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied! Admin only.', 'danger')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get all data
    users = conn.execute('SELECT * FROM users').fetchall()
    students = conn.execute('SELECT * FROM students').fetchall()
    results = conn.execute('SELECT * FROM results').fetchall()
    
    conn.close()
    
    return render_template('admin_data.html', 
                         users=users, 
                         students=students, 
                         results=results)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
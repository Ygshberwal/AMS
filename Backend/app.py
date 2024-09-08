from flask import Flask, request, redirect, url_for, session, render_template, flash
import requests
from werkzeug.utils import secure_filename
import sqlite3
import os
import bcrypt
import re

# Specify the path to your templates and static folders
app = Flask(__name__, 
            template_folder='../Frontend/templates', 
            static_folder='../Frontend/static')
app.secret_key = 'your_secret_key'

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rollno TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            program TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Create instructors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instructors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Password validation function
def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search("[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search("[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search("[0-9]", password):
        return "Password must contain at least one digit."
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."
    return None

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')  # Fetch the selected role (student or teacher)
        email = request.form.get('email')  # Fetch the email
        password = request.form.get('password')  # Fetch the password
        print("Role:", role, "Email:", email)

        conn = sqlite3.connect('ams.db')
        cursor = conn.cursor()

        # Check which role is selected and query the appropriate table
        if role == "student":
            # Query the students table
            cursor.execute('SELECT * FROM students WHERE email = ?', (email,))
            user = cursor.fetchone()
        elif role == "teacher":
            # Query the instructors table
            cursor.execute('SELECT * FROM instructors WHERE email = ?', (email,))
            user = cursor.fetchone()

        conn.close()

        # Check if the user exists and if the password is correct
        if user and bcrypt.checkpw(password.encode('utf-8'), user[4].encode('utf-8')):  # Assuming password is in 5th column
            session['email'] = email
            session['role'] = role
            session['name'] = user[1] 
            print(f"Login successful as {role}")
            return redirect(url_for('dashboard'))
        else:
            print('Invalid credentials')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role')  # Safely access 'role'
        
        if role == "student":
            rollno = request.form.get('rollno')
            name = request.form.get('name')
            program = request.form.get('program')
            email = request.form.get('email')
            password = request.form.get('password')
            print(name, rollno)
            
            # Validate and hash the password
            validation_error = validate_password(password)
            if validation_error:
                print(validation_error)
                return redirect(url_for('register'))

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            try:
                conn = sqlite3.connect('ams.db')
                cursor = conn.cursor()
                cursor.execute('INSERT INTO students (rollno, name, program, email, password) VALUES (?, ?, ?, ?, ?)', 
                               (rollno, name, program, email, hashed_password))
                conn.commit()
                conn.close()
                print('Registration successful! Please log in.')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                print('Username already exists')
                return redirect(url_for('register'))

        elif role == "teacher":
            name = request.form.get('name')
            department = request.form.get('department')
            email = request.form.get('email')
            password = request.form.get('password')

            # Validate and hash the password
            validation_error = validate_password(password)
            if validation_error:
                print(validation_error)
                return redirect(url_for('register'))

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            try:
                conn = sqlite3.connect('ams.db')
                cursor = conn.cursor()
                cursor.execute('INSERT INTO instructors (name, department, email, password) VALUES (?, ?, ?, ?)', 
                               (name, department, email, hashed_password))
                conn.commit()
                conn.close()
                print('Registration successful! Please log in.')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                print('Username already exists')
                return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    role = session['role']
    if role == 'teacher':
        return render_template('dashboard_teacher.html')
    elif role == 'student':
        return render_template('dashboard_student.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('email', None)
    session.pop('role', None)
    return redirect(url_for('login'))

# Define where you want to save the uploaded files
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('ams.db')
    conn.row_factory = sqlite3.Row
    return conn



# Check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to handle form submission and file upload
@app.route('/upload', methods=['POST'])
def upload_video():
    course_code = request.form['course_code']
    date = request.form['date']

    # Check if a video file is in the request
    if 'video' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['video']

    # If no file is selected
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    # If the file is allowed, save it
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        flash('File successfully uploaded')

        # Prepare the file for the API request
        with open(filepath, 'rb') as f:
            files = {'video_file': (filename, f, file.mimetype)}
            api_url = "http://192.168.154.31:8000/run-for-video-file/"
            response = requests.post(api_url, files=files)
            print(response)

        # Assuming response contains a list of student roll numbers
        if response.status_code == 200:
            student_rollnos = response.json()  # Assume the API returns JSON with a list of roll numbers
            save_attendance(course_code, date, student_rollnos['matched_roll_nos'])
            flash('Attendance saved successfully')

        return redirect(url_for('upload_success', filename=filename))

    flash('File type not allowed')
    return redirect(request.url)

# Function to save attendance to the database
def save_attendance(course_code, date, student_rollnos):
    conn = get_db_connection()
    cursor = conn.cursor()
    print(student_rollnos)

    for rollno in student_rollnos:
        cursor.execute(
            'INSERT INTO attendance (s_rollno, c_id, i_id, lecture_date, status) VALUES (?, ?, ?, ?, ?)',
            (rollno, course_code, course_code, date, 1)
        )

    conn.commit()
    conn.close()

# Route to show upload success message
@app.route('/upload_success/<filename>')
def upload_success(filename):
    return f'File {filename} uploaded successfully and attendance saved!'

if __name__ == '__main__':
    if not os.path.exists('users.db'):
        init_db()  # Initialize the database if it doesn't exist
    app.run(debug=True)


import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from utils.parser import extract_text_from_pdf, extract_text_from_docx
from skill_extractor import extract_skills_qualifications
from matcher import match_roles
import secrets
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from recommender import analyze_resume
from recommender import recommend_study_materials, recommend_certification_courses, recommend_interview_tips

# === Flask Setup ===
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

db_host = "localhost"
db_user = "root"
db_password = ""
db_name = "flask_login_db"

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# === DB Connection ===
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="flask_login_db"
    )


# === Helper to check file type ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# === Resume Text Extractor ===
def extract_text_from_resume(filepath):
    if filepath.endswith('.pdf'):
        return extract_text_from_pdf(filepath)
    elif filepath.endswith('.docx'):
        return extract_text_from_docx(filepath)
    else:
        return "sample text from resume"

# === Login Page ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            print("Login successful")  # DEBUG
            cursor.close()
            conn.close()
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials", "danger")
            print("Login failed")  # DEBUG
            cursor.close()
            conn.close()

    return render_template('login.html')

# === Register Page ===
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Basic password match check
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Connect to DB
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()

            # Check if username already exists
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                flash('Username already exists. Please choose another.', 'warning')
                cursor.close()
                conn.close()
                return redirect(url_for('register'))

            # Insert new user into database
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password)
            )
            conn.commit()

            cursor.close()
            conn.close()

            flash('Registered successfully! Please login.', 'success')
            return redirect(url_for('login', registered='true'))

            flash('Database connection error', 'danger')

    return render_template('register.html')
# === Home Page ===
# === Home Page ===
@app.route('/index', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        file = request.files.get('resume')
        if not file or file.filename == '':
            return render_template('index.html', username=session['username'], error="No file selected")

        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            resume_text = extract_text_from_resume(filepath)
            if not resume_text.strip():
                return render_template('index.html', username=session['username'], error="Resume is empty")

            skills, qualifications = extract_skills_qualifications(resume_text)

            return render_template('index.html', 
                                   username=session['username'],
                                   skills=skills,
                                   qualifications=qualifications,
                                   filename=filename)

    return render_template('index.html',
                           username=session['username'],
                           skills=None,
                           qualifications=None,
                           error=None)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# === Forgot Password ===
@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

# === Resume Analyze API ===
@app.route('/analyze_resume', methods=['POST'])
def analyze_resume_route():
    data = request.get_json()
    resume_text = data.get('resume_text', '')

    if not resume_text.strip():
        return jsonify({"error": "Resume content is empty"}), 400

    skills, qualifications = extract_skills_qualifications(resume_text)
    results = match_roles(skills, qualifications)

    return jsonify({
        "skills": skills,
        "qualifications": qualifications,
        "results": results
    })
@app.route('/recommend', methods=['POST'])
def recommend():
    if 'username' not in session:
        return redirect(url_for('login'))

    filename = request.form.get('filename')
    if not filename:
        return render_template('recommendation.html', username=session['username'], error="No file info provided")

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return render_template('recommendation.html', username=session['username'], error="File not found")

    resume_text = extract_text_from_resume(filepath)
    if not resume_text.strip():
        return render_template('recommendation.html', username=session['username'], error="Resume is empty or unreadable")

    # 🔍 Analyze resume
    results = analyze_resume(resume_text)

    if "error" in results:
        return render_template('recommendation.html', username=session['username'], error=results["error"])

    return render_template(
    'recommendation.html',
    username=session.get('username'),
    job_roles=results['job_roles'],
    study_materials=results['study_materials'],
    certifications=results['certifications'],
    interview_tips=results['interview_tips']
)


@app.route('/')
def index():
    return redirect(url_for('login'))  # or 'register' if you prefer

if __name__ == '__main__':
    app.run(debug=True)

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from utils.parser import extract_text_from_pdf, extract_text_from_docx
from skill_extractor import extract_skills_qualifications
from matcher import match_roles
import secrets
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from recommender import analyze_resume
from recommender import recommend_study_materials, recommend_certification_courses, recommend_interview_tips

# === Flask Setup ===
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

db_host = "localhost"
db_user = "root"
db_password = ""
db_name = "flask_login_db"

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# === DB Connection ===
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="flask_login_db"
    )


# === Helper to check file type ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# === Resume Text Extractor ===
def extract_text_from_resume(filepath):
    if filepath.endswith('.pdf'):
        return extract_text_from_pdf(filepath)
    elif filepath.endswith('.docx'):
        return extract_text_from_docx(filepath)
    else:
        return "sample text from resume"

# === Login Page ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            print("Login successful")  # DEBUG
            cursor.close()
            conn.close()
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials", "danger")
            print("Login failed")  # DEBUG
            cursor.close()
            conn.close()

    return render_template('login.html')

# === Register Page ===
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Basic password match check
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Connect to DB
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()

            # Check if username already exists
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                flash('Username already exists. Please choose another.', 'warning')
                cursor.close()
                conn.close()
                return redirect(url_for('register'))

            # Insert new user into database
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password)
            )
            conn.commit()

            cursor.close()
            conn.close()

            flash('Registered successfully! Please login.', 'success')
            return redirect(url_for('login', registered='true'))

            flash('Database connection error', 'danger')

    return render_template('register.html')
# === Home Page ===
# === Home Page ===
@app.route('/index', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        file = request.files.get('resume')
        if not file or file.filename == '':
            return render_template('index.html', username=session['username'], error="No file selected")

        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            resume_text = extract_text_from_resume(filepath)
            if not resume_text.strip():
                return render_template('index.html', username=session['username'], error="Resume is empty")

            skills, qualifications = extract_skills_qualifications(resume_text)

            return render_template('index.html', 
                                   username=session['username'],
                                   skills=skills,
                                   qualifications=qualifications,
                                   filename=filename)

    return render_template('index.html',
                           username=session['username'],
                           skills=None,
                           qualifications=None,
                           error=None)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# === Forgot Password ===
@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

# === Resume Analyze API ===
@app.route('/analyze_resume', methods=['POST'])
def analyze_resume_route():
    data = request.get_json()
    resume_text = data.get('resume_text', '')

    if not resume_text.strip():
        return jsonify({"error": "Resume content is empty"}), 400

    skills, qualifications = extract_skills_qualifications(resume_text)
    results = match_roles(skills, qualifications)

    return jsonify({
        "skills": skills,
        "qualifications": qualifications,
        "results": results
    })
@app.route('/recommend', methods=['POST'])
def recommend():
    if 'username' not in session:
        return redirect(url_for('login'))

    filename = request.form.get('filename')
    if not filename:
        return render_template('recommendation.html', username=session['username'], error="No file info provided")

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return render_template('recommendation.html', username=session['username'], error="File not found")

    resume_text = extract_text_from_resume(filepath)
    if not resume_text.strip():
        return render_template('recommendation.html', username=session['username'], error="Resume is empty or unreadable")

    # 🔍 Analyze resume
    results = analyze_resume(resume_text)

    if "error" in results:
        return render_template('recommendation.html', username=session['username'], error=results["error"])

    return render_template(
    'recommendation.html',
    username=session.get('username'),
    job_roles=results['job_roles'],
    study_materials=results['study_materials'],
    certifications=results['certifications'],
    interview_tips=results['interview_tips']
)


@app.route('/')
def index():
    return redirect(url_for('login'))  # or 'register' if you prefer

if __name__ == '__main__':
    app.run(debug=True)


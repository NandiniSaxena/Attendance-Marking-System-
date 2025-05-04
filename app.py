import os
import cv2
import numpy as np
import face_recognition
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
KNOWN_FACES_DIR = 'known'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg'}
ATTENDANCE_FILE = 'attendance.csv'  # Store attendance in a CSV file

# Function to load known faces
def load_known_faces():
    known_encodings = []
    known_names = []
    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.endswith((".jpg", ".png")):
            image_path = os.path.join(KNOWN_FACES_DIR, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(os.path.splitext(filename)[0])
            else:
                print(f"[WARNING] No face found in: {filename}")
    return known_encodings, known_names

known_encodings, known_names = load_known_faces()

# Function to check if the uploaded image contains a face and return the name
def recognize_face(image):
    encodings = face_recognition.face_encodings(image)
    if encodings:
        for encoding in encodings:
            matches = face_recognition.compare_faces(known_encodings, encoding)
            if True in matches:
                first_match_index = matches.index(True)
                return known_names[first_match_index]
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        session['user'] = {'username': username, 'role': role}
        return redirect(url_for(f'{role}_dashboard'))
    return render_template('login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/student_dashboard')
def student_dashboard():
    # Load attendance data for the student
    username = session['user']['username']
    attendance_data = get_attendance_for_student(username)
    return render_template('student_dashboard.html', attendance_data=attendance_data)

@app.route('/teacher_dashboard')
def teacher_dashboard():
    return render_template('teacher_dashboard.html')

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(KNOWN_FACES_DIR, filename)
            file.save(file_path)
            # Add student to the list
            known_encodings, known_names = load_known_faces()
            return redirect(url_for('teacher_dashboard'))
    return render_template('add_student.html')

@app.route('/capture_attendance', methods=['POST'])
def capture_attendance():
    image_file = request.files['image']
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)

        image = face_recognition.load_image_file(image_path)
        name = recognize_face(image)
        if name:
            # Mark attendance for the student
            mark_attendance(name)
            return jsonify(name=name)
    return jsonify(name=None)

# Helper function to check file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to mark attendance
def mark_attendance(name):
    with open(ATTENDANCE_FILE, 'a') as file:
        date = datetime.now().strftime('%Y-%m-%d')
        time = datetime.now().strftime('%H:%M:%S')
        file.write(f"{date},{name},{time}\n")

# Function to get attendance for a specific student
def get_attendance_for_student(student_name):
    attendance = []
    with open(ATTENDANCE_FILE, 'r') as file:
        for line in file:
            date, name, time = line.strip().split(',')
            if name == student_name:
                attendance.append({'date': date, 'time': time})
    return attendance

# Function to filter attendance by date range
@app.route('/filter_attendance', methods=['POST'])
def filter_attendance():
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    filtered_attendance = []

    with open(ATTENDANCE_FILE, 'r') as file:
        for line in file:
            date, name, time = line.strip().split(',')
            if start_date <= date <= end_date:
                filtered_attendance.append({'date': date, 'name': name, 'time': time})

    return jsonify(filtered_attendance)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, session, send_file, Response
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os
import pandas as pd
from collections import defaultdict
from datetime import datetime
import face_recognition
import cv2

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = generate_password_hash('admin123')  # change password as needed

# Paths
attendance_file = 'attendance.csv'
known_faces_dir = 'known'

# Route: Admin Login Page
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Invalid credentials.")
    return render_template('admin_login.html')

# Route: Admin Dashboard
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    # Process attendance data
    group_by = request.args.get('group_by', 'day')
    chart_type = request.args.get('chart_type', 'bar')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    chart_data = []
    records = []
    
    if os.path.exists(attendance_file):
        with open(attendance_file, 'r') as f:
            reader = csv.DictReader(f)
            raw_data = [row for row in reader]
            grouped = defaultdict(lambda: defaultdict(int))
            total_per_student = defaultdict(int)

            for row in raw_data:
                date, name, time = row.get('date'), row.get('name'), row.get('time')
                if date and name and time:
                    if start_date and date < start_date:
                        continue
                    if end_date and date > end_date:
                        continue
                    
                    date_obj = datetime.strptime(date, '%Y-%m-%d')
                    if group_by == 'week':
                        key = f"Week {date_obj.isocalendar()[1]}"
                    elif group_by == 'month':
                        key = date_obj.strftime('%B')
                    else:
                        key = date
                    
                    grouped[name][key] += 1
                    total_per_student[name] += 1

            for name, group in grouped.items():
                labels = list(group.keys())
                counts = [group[label] for label in labels]
                chart_data.append({"name": name, "labels": labels, "counts": counts, "total": total_per_student[name]})
                
            records = raw_data  # For displaying attendance records
            
    return render_template('admin_dashboard.html',
                           group_by=group_by,
                           chart_type=chart_type,
                           chart_data=chart_data,
                           start_date=start_date,
                           end_date=end_date,
                           records=records)

# Route: Attendance Capture Video Feed
def gen():
    video_capture = cv2.VideoCapture(0)
    known_face_encodings = []
    known_face_names = []

    # Load known faces
    for filename in os.listdir(known_faces_dir):
        if filename.endswith(".jpg") or filename.endswith(".jpeg"):
            img = face_recognition.load_image_file(f"{known_faces_dir}/{filename}")
            face_encoding = face_recognition.face_encodings(img)[0]
            name = os.path.splitext(filename)[0]  # Extract name from filename
            known_face_encodings.append(face_encoding)
            known_face_names.append(name)

    while True:
        ret, frame = video_capture.read()
        if not ret:
            continue
        rgb_frame = frame[:, :, ::-1]  # Convert BGR to RGB

        # Find all face locations and encodings in the current frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # For each face in this frame, see if it's a match for known faces
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            # Draw a rectangle around the face and label it with the name
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

            # If the person is recognized, mark attendance
            if name != "Unknown":
                now = datetime.now()
                date_str = now.strftime("%Y-%m-%d")
                time_str = now.strftime("%H:%M:%S")
                with open(attendance_file, 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow([date_str, name, time_str])

        # Encode the frame in JPEG format and send to browser
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Route: Streaming Video Feed
@app.route('/admin/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route: Export Attendance
@app.route('/admin/export')
def export_attendance():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    if os.path.exists(attendance_file):
        df = pd.read_csv(attendance_file)
        export_path = 'attendance_export.xlsx'
        df.to_excel(export_path, index=False)
        return send_file(export_path, as_attachment=True)

    return "No attendance file found."

# Logout route
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)

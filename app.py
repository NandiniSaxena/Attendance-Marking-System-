# from flask import Flask, render_template, request, redirect, url_for, session, send_file, Response
# from werkzeug.security import generate_password_hash, check_password_hash
# import csv
# import os
# import pandas as pd
# from collections import defaultdict
# from datetime import datetime
# import face_recognition
# import cv2

# app = Flask(__name__)
# app.secret_key = 'supersecretkey'

# # Admin credentials
# ADMIN_USERNAME = 'admin'
# ADMIN_PASSWORD_HASH = generate_password_hash('admin123')  # change password as needed

# # Paths
# attendance_file = 'attendance.csv'
# known_faces_dir = 'known'

# # ➤ New Route: Home Page ("/")
# @app.route('/')
# def home():
#     return redirect(url_for('admin_login'))

# # ➤ New Route: Placeholder for Predictions
# @app.route('/predictions', methods=['GET', 'POST'])
# def predictions():
#     return "Prediction functionality will be added here."

# # Admin Login Page
# @app.route('/admin', methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
#             session['admin'] = True
#             return redirect(url_for('admin_dashboard'))
#         else:
#             return render_template('admin_login.html', error="Invalid credentials.")
#     return render_template('admin_login.html')

# # Admin Dashboard
# @app.route('/admin/dashboard', methods=['GET', 'POST'])
# def admin_dashboard():
#     if not session.get('admin'):
#         return redirect(url_for('admin_login'))

#     group_by = request.args.get('group_by', 'day')
#     chart_type = request.args.get('chart_type', 'bar')
#     start_date = request.args.get('start_date')
#     end_date = request.args.get('end_date')

#     chart_data = []
#     records = []

#     if os.path.exists(attendance_file):
#         with open(attendance_file, 'r') as f:
#             reader = csv.DictReader(f)
#             raw_data = [row for row in reader]
#             grouped = defaultdict(lambda: defaultdict(int))
#             total_per_student = defaultdict(int)

#             for row in raw_data:
#                 date, name, time = row.get('date'), row.get('name'), row.get('time')
#                 if date and name and time:
#                     if start_date and date < start_date:
#                         continue
#                     if end_date and date > end_date:
#                         continue

#                     date_obj = datetime.strptime(date, '%Y-%m-%d')
#                     if group_by == 'week':
#                         key = f"Week {date_obj.isocalendar()[1]}"
#                     elif group_by == 'month':
#                         key = date_obj.strftime('%B')
#                     else:
#                         key = date

#                     grouped[name][key] += 1
#                     total_per_student[name] += 1

#             for name, group in grouped.items():
#                 labels = list(group.keys())
#                 counts = [group[label] for label in labels]
#                 chart_data.append({"name": name, "labels": labels, "counts": counts, "total": total_per_student[name]})

#             records = raw_data

#     return render_template('admin_dashboard.html',
#                            group_by=group_by,
#                            chart_type=chart_type,
#                            chart_data=chart_data,
#                            start_date=start_date,
#                            end_date=end_date,
#                            records=records)

# # Attendance Capture Video Feed
# def gen():
#     video_capture = cv2.VideoCapture(0)
#     known_face_encodings = []
#     known_face_names = []

#     for filename in os.listdir(known_faces_dir):
#         if filename.endswith(".jpg") or filename.endswith(".jpeg"):
#             img = face_recognition.load_image_file(f"{known_faces_dir}/{filename}")
#             encodings = face_recognition.face_encodings(img)
#             if encodings:
#                 known_face_encodings.append(encodings[0])
#                 known_face_names.append(os.path.splitext(filename)[0])

#     while True:
#         ret, frame = video_capture.read()
#         if not ret:
#             continue

#         rgb_frame = frame[:, :, ::-1]
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             name = "Unknown"
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
#             cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

#             if name != "Unknown":
#                 now = datetime.now()
#                 date_str = now.strftime("%Y-%m-%d")
#                 time_str = now.strftime("%H:%M:%S")
#                 with open(attendance_file, 'a', newline='') as f:
#                     writer = csv.writer(f)
#                     writer.writerow([date_str, name, time_str])

#         ret, jpeg = cv2.imencode('.jpg', frame)
#         if not ret:
#             continue
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

# # Video Feed Stream
# @app.route('/admin/video_feed')
# def video_feed():
#     return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

# # Export Attendance to Excel
# @app.route('/admin/export')
# def export_attendance():
#     if not session.get('admin'):
#         return redirect(url_for('admin_login'))

#     if os.path.exists(attendance_file):
#         df = pd.read_csv(attendance_file)
#         export_path = 'attendance_export.xlsx'
#         df.to_excel(export_path, index=False)
#         return send_file(export_path, as_attachment=True)

#     return "No attendance file found."

# # Logout
# @app.route('/logout')
# def logout():
#     session.pop('admin', None)
#     return redirect(url_for('admin_login'))

# # Run Flask App
# if __name__ == '__main__':
#     app.run(debug=True)





# from flask import Flask, render_template, request, redirect, url_for, session, send_file, Response
# from werkzeug.security import generate_password_hash, check_password_hash
# import csv
# import os
# import pandas as pd
# from collections import defaultdict
# from datetime import datetime
# import face_recognition
# import cv2
# import threading

# app = Flask(__name__)
# app.secret_key = 'supersecretkey'

# # Admin credentials
# ADMIN_USERNAME = 'admin'
# ADMIN_PASSWORD_HASH = generate_password_hash('admin123')

# # Paths
# attendance_file = 'attendance.csv'
# known_faces_dir = 'known'

# # Load known face encodings once
# known_face_encodings = []
# known_face_names = []
# for filename in os.listdir(known_faces_dir):
#     if filename.endswith(".jpg") or filename.endswith(".jpeg"):
#         img = face_recognition.load_image_file(f"{known_faces_dir}/{filename}")
#         encodings = face_recognition.face_encodings(img)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(os.path.splitext(filename)[0])

# # ➤ Home Redirect
# @app.route('/')
# def home():
#     return redirect(url_for('admin_login'))

# # ➤ Placeholder for Predictions
# @app.route('/predictions', methods=['GET', 'POST'])
# def predictions():
#     return "Prediction functionality will be added here."

# # Admin Login Page
# @app.route('/admin', methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
#             session['admin'] = True
#             return redirect(url_for('admin_dashboard'))
#         else:
#             return render_template('admin_login.html', error="Invalid credentials.")
#     return render_template('admin_login.html')

# # Admin Dashboard
# @app.route('/admin/dashboard', methods=['GET', 'POST'])
# def admin_dashboard():
#     if not session.get('admin'):
#         return redirect(url_for('admin_login'))

#     group_by = request.args.get('group_by', 'day')
#     chart_type = request.args.get('chart_type', 'bar')
#     start_date = request.args.get('start_date')
#     end_date = request.args.get('end_date')

#     chart_data = []
#     records = []

#     if os.path.exists(attendance_file):
#         with open(attendance_file, 'r') as f:
#             reader = csv.DictReader(f)
#             raw_data = [row for row in reader]
#             grouped = defaultdict(lambda: defaultdict(int))
#             total_per_student = defaultdict(int)

#             for row in raw_data:
#                 date, name, time = row.get('date'), row.get('name'), row.get('time')
#                 if date and name and time:
#                     if start_date and date < start_date:
#                         continue
#                     if end_date and date > end_date:
#                         continue

#                     date_obj = datetime.strptime(date, '%Y-%m-%d')
#                     if group_by == 'week':
#                         key = f"Week {date_obj.isocalendar()[1]}"
#                     elif group_by == 'month':
#                         key = date_obj.strftime('%B')
#                     else:
#                         key = date

#                     grouped[name][key] += 1
#                     total_per_student[name] += 1

#             for name, group in grouped.items():
#                 labels = list(group.keys())
#                 counts = [group[label] for label in labels]
#                 chart_data.append({"name": name, "labels": labels, "counts": counts, "total": total_per_student[name]})

#             records = raw_data

#     return render_template('admin_dashboard.html',
#                            group_by=group_by,
#                            chart_type=chart_type,
#                            chart_data=chart_data,
#                            start_date=start_date,
#                            end_date=end_date,
#                            records=records)

# # Global video capture
# video_capture = cv2.VideoCapture(0)
# seen_today = set()

# # Attendance Capture
# frame_skip = 3
# def gen():
#     frame_count = 0
#     while True:
#         ret, frame = video_capture.read()
#         if not ret:
#             continue

#         frame_count += 1
#         if frame_count % frame_skip != 0:
#             continue

#         rgb_frame = frame[:, :, ::-1]
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             name = "Unknown"
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
#             cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

#             if name != "Unknown":
#                 now = datetime.now()
#                 date_str = now.strftime("%Y-%m-%d")
#                 time_str = now.strftime("%H:%M:%S")
#                 record_id = f"{date_str}_{name}"
#                 if record_id not in seen_today:
#                     seen_today.add(record_id)
#                     with open(attendance_file, 'a', newline='') as f:
#                         writer = csv.writer(f)
#                         writer.writerow([date_str, name, time_str])

#         ret, jpeg = cv2.imencode('.jpg', frame)
#         if not ret:
#             continue
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

# @app.route('/admin/video_feed')
# def video_feed():
#     return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/admin/export')
# def export_attendance():
#     if not session.get('admin'):
#         return redirect(url_for('admin_login'))

#     if os.path.exists(attendance_file):
#         df = pd.read_csv(attendance_file)
#         export_path = 'attendance_export.xlsx'
#         df.to_excel(export_path, index=False)
#         return send_file(export_path, as_attachment=True)

#     return "No attendance file found."

# @app.route('/logout')
# def logout():
#     session.pop('admin', None)
#     return redirect(url_for('admin_login'))

# if __name__ == '__main__':
#     app.run(debug=True)






from flask import Flask, render_template, request, redirect, url_for, session, send_file, Response
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os
import pandas as pd
from collections import defaultdict
from datetime import datetime
import face_recognition
import cv2
import threading
import queue
import time

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = generate_password_hash('admin123')

# Paths
attendance_file = 'attendance.csv'
known_faces_dir = 'known'

# Load known face encodings once
known_face_encodings = []
known_face_names = []
for filename in os.listdir(known_faces_dir):
    if filename.endswith(".jpg") or filename.endswith(".jpeg"):
        img = face_recognition.load_image_file(f"{known_faces_dir}/{filename}")
        encodings = face_recognition.face_encodings(img)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(os.path.splitext(filename)[0])

# Global video capture
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    print("Error: Could not open camera.")
    exit(1)

# Frame buffer and synchronization
latest_frame = None
frame_lock = threading.Lock()
seen_today = set()
attendance_queue = queue.Queue()
running = True

# Frame capture thread
def capture_frames():
    global latest_frame, running
    while running:
        ret, frame = video_capture.read()
        if not ret:
            time.sleep(0.01)
            continue
        # Resize frame for efficiency
        frame = cv2.resize(frame, (640, 480))
        with frame_lock:
            latest_frame = frame
        time.sleep(0.033)  # Target ~30 FPS

# Face recognition thread
def process_faces():
    global running
    frame_count = 0
    frame_skip = 3
    while running:
        with frame_lock:
            if latest_frame is None:
                time.sleep(0.01)
                continue
            frame = latest_frame.copy()
        
        frame_count += 1
        if frame_count % frame_skip != 0:
            time.sleep(0.1)
            continue

        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame, model="small")  # Faster model
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            if name != "Unknown":
                now = datetime.now()
                date_str = now.strftime("%Y-%m-%d")
                time_str = now.strftime("%H:%M:%S")
                record_id = f"{date_str}_{name}"
                if record_id not in seen_today:
                    seen_today.add(record_id)
                    attendance_queue.put([date_str, name, time_str])

        time.sleep(0.1)  # Limit face recognition to ~10 FPS

# Attendance logging thread
def log_attendance():
    while running:
        try:
            record = attendance_queue.get(timeout=1)
            with open(attendance_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(record)
            attendance_queue.task_done()
        except queue.Empty:
            continue

# Start background threads
threading.Thread(target=capture_frames, daemon=True).start()
threading.Thread(target=process_faces, daemon=True).start()
threading.Thread(target=log_attendance, daemon=True).start()

# MJPEG streaming
def gen():
    while True:
        with frame_lock:
            if latest_frame is None:
                continue
            frame = latest_frame.copy()
        
        # Add face rectangles and names (optional, for visual feedback)
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame, model="small")
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, "Detecting...", (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

        ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        time.sleep(0.033)  # Target ~30 FPS

# Routes
@app.route('/')
def home():
    return redirect(url_for('admin_login'))

@app.route('/predictions', methods=['GET', 'POST'])
def predictions():
    return "Prediction functionality will be added here."

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

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

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

            records = raw_data

    return render_template('admin_dashboard.html',
                           group_by=group_by,
                           chart_type=chart_type,
                           chart_data=chart_data,
                           start_date=start_date,
                           end_date=end_date,
                           records=records)

@app.route('/admin/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

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

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.teardown_appcontext
def cleanup(exception=None):
    global running
    running = False
    video_capture.release()

if __name__ == '__main__':
    app.run(debug=False, threaded=True)  # Disable debug to reduce overhead
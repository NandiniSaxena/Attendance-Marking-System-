import os
import cv2
import csv
import datetime
import face_recognition
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

# Folder with known faces
known_faces_dir = "known"
known_face_encodings = []
known_face_names = []

# Load known faces
for filename in os.listdir(known_faces_dir):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image_path = os.path.join(known_faces_dir, filename)
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(os.path.splitext(filename)[0])

if not known_face_encodings:
    raise Exception("No known faces found.")

# Initialize attendance
attendance_file = "attendance.csv"
today = datetime.date.today().strftime("%Y-%m-%d")
marked_today = set()

if not os.path.exists(attendance_file):
    with open(attendance_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Name", "Time"])

# Load already marked names for today
with open(attendance_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if row and row[0] == today:
            marked_today.add(row[1])

video_capture = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = video_capture.read()
        if not success:
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small)
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match = face_distances.argmin()
            if matches[best_match]:
                name = known_face_names[best_match]

            if name != "Unknown" and name not in marked_today:
                marked_today.add(name)
                now = datetime.datetime.now().strftime("%H:%M:%S")
                with open(attendance_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([today, name, now])
                print(f"Marked {name} present at {now}")

            # Draw box
            top, right, bottom, left = [v * 4 for v in face_location]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/')
def index():
    return render_template('index.html', students=known_face_names)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/attendance_today')
def attendance_today():
    records = []
    with open(attendance_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0] == today:
                records.append({"name": row[1], "time": row[2]})
    return jsonify(records)

if __name__ == "__main__":
    app.run(debug=True)






# # import os
# # import cv2
# # import face_recognition
# # from flask import Flask, render_template, Response

# # app = Flask(__name__)

# # # 🔄 [CHANGE #1]: Load all known face images from a folder
# # known_face_encodings = []
# # known_face_names = []

# # known_faces_dir = "D:/newaiml/Attendance-Marking-System-/known"

# # for filename in os.listdir(known_faces_dir):
# #     if filename.endswith(".jpg") or filename.endswith(".png"):
# #         image_path = os.path.join(known_faces_dir, filename)
# #         image = face_recognition.load_image_file(image_path)
# #         encodings = face_recognition.face_encodings(image)
# #         if encodings:
# #             known_face_encodings.append(encodings[0])
# #             # Use filename (without extension) as name
# #             known_face_names.append(os.path.splitext(filename)[0])

# # if not known_face_encodings:
# #     print("No faces found in the known folder.")
# #     exit()

# # # 🎥 [UNCHANGED]: Initialize the camera
# # video_capture = cv2.VideoCapture(0)

# # # 🔁 [MODIFIED]: Support multiple face matches
# # def generate_frames():
# #     while True:
# #         ret, frame = video_capture.read()
# #         if not ret:
# #             break

# #         # Resize for performance
# #         small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
# #         rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

# #         face_locations = face_recognition.face_locations(rgb_small)
# #         face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

# #         face_names = []  # 🆕 Store names for current frame

# #         for face_encoding in face_encodings:
# #             # Compare with all known faces
# #             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
# #             name = "Unknown"

# #             # Use the known face with the smallest distance (most confident match)
# #             face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
# #             if len(face_distances) > 0:
# #                 best_match_index = face_distances.argmin()
# #                 if matches[best_match_index]:
# #                     name = known_face_names[best_match_index]

# #             face_names.append(name)

# #         # Draw rectangles and names
# #         for (top, right, bottom, left), name in zip(face_locations, face_names):
# #             top *= 4
# #             right *= 4
# #             bottom *= 4
# #             left *= 4

# #             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
# #             cv2.putText(frame, name, (left, top - 10),
# #                         cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

# #         # Convert to JPEG for streaming
# #         ret, buffer = cv2.imencode('.jpg', frame)
# #         frame = buffer.tobytes()

# #         yield (b'--frame\r\n'
# #                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# # # 🧭 Flask routes
# # @app.route('/')
# # def index():
# #     return render_template('index.html')

# # @app.route('/video_feed')
# # def video_feed():
# #     return Response(generate_frames(),
# #                     mimetype='multipart/x-mixed-replace; boundary=frame')

# # # 🚀 Run the app
# # if __name__ == '__main__':
# #     app.run(debug=True)


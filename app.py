import os
import cv2
import face_recognition
from flask import Flask, render_template, Response

app = Flask(__name__)

# Load a known image and encode it
known_image = face_recognition.load_image_file("D:/newaiml/known/aryan.jpg")
known_face_encodings = face_recognition.face_encodings(known_image)

if len(known_face_encodings) == 0:
    print("No faces found in the known image.")
    exit()

known_face_encoding = known_face_encodings[0]

# Initialize the camera
video_capture = cv2.VideoCapture(0)

def generate_frames():
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        
        # Resize the frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Find faces and their encodings
        face_locations = face_recognition.face_locations(rgb_small)
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces([known_face_encoding], face_encoding)
            name = "Unknown"

            if True in matches:
                name = "Aryan"

            # Draw rectangle around face and put name text
            for (top, right, bottom, left), name in zip(face_locations, [name] * len(face_encodings)):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

        # Convert the frame to JPEG for streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)




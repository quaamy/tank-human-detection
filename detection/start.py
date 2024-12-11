from flask import Flask, request, Response, render_template_string, send_from_directory
import face_recognition
import cv2
import numpy as np
from datetime import datetime
import hashlib
import os
import torch

app = Flask(__name__)

# Put at least 1 known_images. Change Clark.jpg, Clark
# video_capture = cv2.VideoCapture(0) value 0 means webcam
# SAVE_DIR is the directory where the images will be saved locally on the computer

SAVE_DIR = 'detection/detected_images/'

known_images = [("clark.png", "Clark")]
known_face_encodings = []
known_face_names = []

for filename, name in known_images:
    image = face_recognition.load_image_file(filename)
    face_encodings = face_recognition.face_encodings(image)
    if len(face_encodings) > 0:
        known_face_encodings.append(face_encodings[0])
        known_face_names.append(name)
    else:
        print(f"No faces found in {filename}")

saved_known_face_encodings = set()

def hash_face_encoding(face_encoding):
    return hashlib.sha256(face_encoding).hexdigest()

def gen_frames():
    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FPS, 15)
    saved_image = False
    while True:
        success, frame = video_capture.read()
        if not success:
            break
        else:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            face_names = []
            face_colors = []

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                color = (0, 0, 255)

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    color = (0, 255, 0)

                face_names.append(name)
                face_colors.append(color)

            for (top, right, bottom, left), name, color, face_encoding in zip(face_locations, face_names, face_colors, face_encodings):
                if name != "Unknown" and not saved_image:
                    face_encoding_hash = hash_face_encoding(face_encoding)
                    if face_encoding_hash not in saved_known_face_encodings:
                        saved_known_face_encodings.add(face_encoding_hash)

                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        full_image_filename = os.path.join(SAVE_DIR, f"full_{name}_{timestamp}.jpg")
                        face_crop = frame[top:bottom, left:right]
                        zoomed_image_filename = os.path.join(SAVE_DIR, f"zoomed_{name}_{timestamp}.jpg")

                        cv2.imwrite(full_image_filename, frame) 
                        print(f"Saved full image: {full_image_filename}")
                    
                        cv2.imwrite(zoomed_image_filename, face_crop) 
                        print(f"Saved zoomed image: {zoomed_image_filename}")

                        saved_image = True

                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.rectangle(frame, (left, bottom - 30), (right, bottom), color, cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def gen_person_count_frames():
    video_capture = cv2.VideoCapture(0)
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=True) 
    while True:
        success, frame = video_capture.read()
        if not success:
            break
        else:
            results = model(frame)
            bboxes = results.xyxy[0].cpu().numpy()
            conf_threshold = 0.3
            bboxes = [bbox for bbox in bboxes if bbox[4] >= conf_threshold]
            count_persons = len(bboxes)

            for bbox in bboxes:
                x1, y1, x2, y2 = map(int, bbox[:4])
                cls = int(bbox[5])
                label = results.names[cls]
                color = (0, 255, 0)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), color, cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, label, (x1 + 6, y2 - 6), font, 1.0, (255, 255, 255), 1)
            
            cv2.putText(frame, f"Persons: {count_persons}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                    margin: 0;
                    padding: 20px;
                }
                h1 {
                    color: #333;
                    text-align: center;
                }
                ul {
                    list-style-type: none;
                    padding: 0;
                }
                li {
                    margin: 10px 0;
                }
                a {
                    display: inline-block;
                    padding: 10px 20px;
                    text-decoration: none;
                    color: white;
                    background-color: #007bff;
                    border-radius: 5px;
                    transition: background-color 0.3s ease;
                }
                a:hover {
                    background-color: #0056b3;
                }
            </style>
            <title>Routes</title>
        </head>
        <body>
            <h1>Routes</h1> 
            <ul> 
                <li><a href="/face_recognition">Face Recognition</a></li>
                <li><a href="/person_count">Person Count</a></li>
                <li><a href="/images">Saved Images</a></li>
            </ul> 
        </body>
        </html>
    """)

@app.route('/face_recognition')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/person_count')
def person_count_feed():
    return Response(gen_person_count_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/images')
def list_images():
    images = os.listdir(SAVE_DIR)
    images_html = ''.join([f'<li><a href="/images/{img}">{img}</a></li>' for img in images])
    return render_template_string(f"""
        <h1>Saved Images</h1>
        <ul>
            {images_html}
        </ul>
    """)

if __name__ == '__main__':
    app.run(debug=True)


from flask import Flask, request, Response, render_template_string, send_from_directory
import face_recognition
import cv2
import numpy as np
from datetime import datetime
import hashlib
import os

app = Flask(__name__)

# Put at least 1 known_images. Change Clark.jpg, Clark
# video_capture = cv2.VideoCapture(0) value 0 means webcam
# SAVE_DIR is the directory where the images will be saved locally on the computer

SAVE_DIR = 'detection/detected_images/'

known_images = [("clark.jpg", "Clark")]
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

                        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                        cv2.rectangle(frame, (left, bottom - 30), (right, bottom), color, cv2.FILLED)
                        font = cv2.FONT_HERSHEY_DUPLEX
                        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        full_image_filename = os.path.join(SAVE_DIR, f"full_{name}_{timestamp}.jpg")
                        face_crop = frame[top:bottom, left:right]
                        zoomed_image_filename = os.path.join(SAVE_DIR, f"zoomed_{name}_{timestamp}.jpg")

                        cv2.imwrite(full_image_filename, frame) 
                        print(f"Saved full image: {full_image_filename}")
                    
                        cv2.imwrite(zoomed_image_filename, face_crop) 
                        print(f"Saved zoomed image: {zoomed_image_filename}")

                        saved_image = True

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template_string("""
        <h1>Routes</h1> 
        <ul> 
            <a href="/video_feed">Video Feed</a>
            <a href="/images">Saved Images</a>
        </ul> 
    """)

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

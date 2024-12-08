import face_recognition
import cv2
import numpy as np
from datetime import datetime
import hashlib

# Add Sample File in the Folder.
# Known images = (Picture/Selfie, Name).
# cv2.VideoCapture(0) = Webcam 
# Saves the image of one known person. 
# Crtl + C or q/Q to end.

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

video_capture = cv2.VideoCapture(0)

if not video_capture.isOpened():
    print("Error: Could not open video.")
else:
    print("Video opened successfully.")

saved_known_face_encodings = set()

def hash_face_encoding(face_encoding):
    return hashlib.sha256(face_encoding).hexdigest()

images_saved = False

while video_capture.isOpened():
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to grab frame or end of video.")
        break  

    rgb_frame = np.ascontiguousarray(frame[:, :, ::-1]) 

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

    if not images_saved:
        for (top, right, bottom, left), name, color, face_encoding in zip(face_locations, face_names, face_colors, face_encodings):
            if name != "Unknown":
                face_encoding_hash = hash_face_encoding(face_encoding)
                if face_encoding_hash not in saved_known_face_encodings:
                    saved_known_face_encodings.add(face_encoding_hash) 

                    print(f"Detected known face {name} at [{top}, {right}, {bottom}, {left}]")
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    cv2.rectangle(frame, (left, bottom - 30), (right, bottom), color, cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    full_image_filename = f"full_{name}_{timestamp}.jpg"
                    cv2.imwrite(full_image_filename, frame)
                    print(f"Saved full image: {full_image_filename} with timestamp: {timestamp}")

                    face_crop = frame[top:bottom, left:right]
                    zoomed_image_filename = f"zoomed_{name}_{timestamp}.jpg"
                    cv2.imwrite(zoomed_image_filename, face_crop)
                    print(f"Saved zoomed image: {zoomed_image_filename} with timestamp: {timestamp}")

                    images_saved = True
                    break


        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

video_capture.release()
cv2.destroyAllWindows()

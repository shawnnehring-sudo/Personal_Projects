import face_recognition
import cv2
import numpy as np

def get_picture():
    cap = cv2.VideoCapture(0)
    pict = None
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow('MyWindow', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            pict = frame.copy()
            cv2.imwrite("pers_pict.jpg", pict)
            break

    cap.release()
    cv2.destroyAllWindows()

    return pict

def compare_picture():
    known_image = face_recognition.load_image_file("frog.jpg")
    unknown_image = face_recognition.load_image_file("pers_pict.jpg")

    known_encodings = face_recognition.face_encodings(known_image)
    unknown_encodings = face_recognition.face_encodings(unknown_image)

    if len(known_encodings) == 0:
        print("❌ No face found in known image (Shawn.jpg)")
        return False

    if len(unknown_encodings) == 0:
        print("❌ No face found in captured image (pers_pict.jpg)")
        return False

    known_encoding = known_encodings[0]
    unknown_encoding = unknown_encodings[0]

    results = face_recognition.compare_faces([known_encoding], unknown_encoding)
    return results[0]

# Run the full process
get_picture()
result = compare_picture()
print("✅ Match found!" if result else "❌ Not a match.")

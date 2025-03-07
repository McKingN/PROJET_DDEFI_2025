import os
import time
import cv2
from fastapi import Request

UPLOAD_FOLDER = "uploaded_images"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

async def take_photo(request: Request):
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Adjust parameters for better face detection
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.3, minNeighbors=5, minSize=(50, 50)
        )

        for x, y, w, h in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        cv2.imshow("Face Detection", frame)
        
        key = cv2.waitKey(1)
        if key & 0xFF in [ord('s'), ord('S'), ord(' ')]:
            print("Prise")
            # Check if there are any faces detected
            if len(faces) == 0:
                cap.release()
                cv2.destroyAllWindows()
                # Return a message indicating no face detected
                return {"message": "Aucun visage détecté de face dans l'image"}
            elif len(faces) >= 2:
                cap.release()
                cv2.destroyAllWindows()
                # Return a message indicating multiple faces detected
                return {"message": "Plusieurs visages sont détectés. Veuillez mettre une image d'un seul visage"}
            else:
                cap.release()
                # Loop over all detected faces
                for i, (x, y, w, h) in enumerate(faces):
                    # Crop the face from the image
                    face = frame[y:y + h, x:x + w]
                    # Resize the face to 100x100 pixels
                    face = cv2.resize(face, (100, 100))
                    # Save the face in a file
                    face_filename = f"face_{i}_{int(time.time())}.png"
                    face_path = os.path.join(UPLOAD_FOLDER, face_filename)
                    cv2.imwrite(face_path, face)
                    cv2.destroyAllWindows()
                    # Return the face path
                    return {"face_path": face_path}
            break

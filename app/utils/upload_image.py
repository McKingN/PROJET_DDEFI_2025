import cv2
import os
import time
import numpy as np
from fastapi import File, UploadFile

UPLOAD_FOLDER = "uploaded_images"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
async def upload_image(file: UploadFile = File(...)):
    # Read the image from the uploaded file
    image = cv2.imdecode(np.frombuffer(file.file.read(), np.uint8), 1)
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if image.shape[:2] == (48, 48):
        # Save the image in a file
        image_filename = f"image_{int(time.time())}.png"
        face_path = os.path.join(UPLOAD_FOLDER, image_filename)
        cv2.imwrite(face_path, image)
        # Return the image path
        return {"face_path": face_path}
        
    else :
        # Load the Haar Cascade classifier for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        # Detect faces in the image
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=3, minSize=(60, 60))
        # Check if there are any faces detected
        if len(faces) == 0:
            # Return a message indicating no face detected
            return {"message": "Aucun visage détecté de face dans l'image"}
        elif len(faces) >= 2:
            # Return a message indicating no face detected
            return {"message": "Plusieurs visages sont détectés. Veuillez mettre une image d'un seul visage"}
        else:
            # Loop over all detected faces
            for i, (x, y, w, h) in enumerate(faces):
                # Crop the face from the image
                face = image[y:y + h, x:x + w]
                # Resize the face to 100x100 pixels
                face = cv2.resize(face, (100, 100))
                # Save the face in a file
                face_filename = f"face_{i}_{int(time.time())}.png"
                face_path = os.path.join(UPLOAD_FOLDER, face_filename)
                cv2.imwrite(face_path, face)
                # Return the face path
                return {"face_path": face_path}

import joblib
import cv2
import numpy as np
from prometheus_client import Counter
from keras.models import load_model

# Créez des compteurs pour chaque émotion
emotion_counters = {
    "Angry": Counter('angry_emotions', 'Number of angry emotions detected'),
    "Disgusted": Counter('disgusted_emotions', 'Number of disgusted emotions detected'),
    "Fearful": Counter('fearful_emotions', 'Number of fearful emotions detected'),
    "Happy": Counter('happy_emotions', 'Number of happy emotions detected'),
    "Neutral": Counter('neutral_emotions', 'Number of neutral emotions detected'),
    "Sad": Counter('sad_emotions', 'Number of sad emotions detected'),
    "Surprised": Counter('surprised_emotions', 'Number of surprised emotions detected'),
}



async def predict_emotion_release(image_path: str):
    emotion_dict = {
        0: "Angry",
        1: "Disgusted",
        2: "Fearful",
        3: "Happy",
        4: "Neutral",
        5: "Sad",
        6: "Surprised",
    }
    model = joblib.load("model/emotion_model copy.joblib")
    image = cv2.imread(image_path)

    # Preprocess the image
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    roi_gray = cv2.resize(gray_image, (48, 48))
    roi_gray = np.expand_dims(np.expand_dims(roi_gray, -1), 0)

    # Predict the emotion
    emotion_prediction = model.predict(roi_gray)
    max_index = int(np.argmax(emotion_prediction))

    # Get the predicted emotion label
    predicted_emotion = emotion_dict[max_index]

    return {"predicted_emotion": predicted_emotion}

async def predict_emotion(image_path: str):
    emotion_dict = {
        0: "Angry",
        1: "Disgusted",
        2: "Fearful",
        3: "Happy",
        4: "Neutral",
        5: "Sad",
        6: "Surprised",
    }
    model_main = joblib.load("model/emotion_model copy.joblib")
    image = cv2.imread(image_path)

    # Preprocess the image
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    roi_gray = cv2.resize(gray_image, (48, 48))
    roi_gray = np.expand_dims(np.expand_dims(roi_gray, -1), 0)

    # Predict the emotion
    emotion_prediction = model_main.predict(roi_gray)
    max_index = int(np.argmax(emotion_prediction))

    # Get the predicted emotion label
    predicted_emotion = emotion_dict[max_index]

    return {"predicted_emotion": predicted_emotion}


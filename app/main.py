# import codecs
# import cv2
# import os
# from fastapi.responses import HTMLResponse
# import numpy as np
# import uvicorn
# from fastapi import FastAPI, File, Request, Response, UploadFile
# from fastapi.staticfiles import StaticFiles
# from prometheus_client import make_asgi_app
# from utils.take_photo_camera import take_photo
# from utils.upload_image import upload_image
# from utils.predict_by_Img_path import predict_emotion
# import metrics_machine_learning as metrics_machine_learning
# from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
# from utils.predict_by_Img_path import emotion_counters






# app = FastAPI()

# metrics_app = make_asgi_app()
# app.mount("/metrics", metrics_app)


# @app.get("/metrics_machine_learning")
# async def metrics():
#     """
#     Endpoint to evaluate machine learning metrics for our model and updated metrics concerned by the way.

#     Returns:
#         Response: The Prometheus-formatted metrics response.
#     """
#     await metrics_machine_learning.main()
#     return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    

# UPLOAD_FOLDER = "uploaded_images"
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# app.mount(
#     "/uploaded_images", StaticFiles(directory=UPLOAD_FOLDER), name="uploaded_images"
# )

# face_cascade = cv2.CascadeClassifier(
#     cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
# )


# @app.get("/predict_from_taken_photo")
# async def predict_from_taken_photo(request: Request):
#     """
#     Endpoint to predict emotion from a photo taken(based on cv2) using the device's camera.

#     Args:
#         request (Request): The FastAPI request object.

#     Returns:
#         Dict[str, Any]: The result of the prediction, including the predicted emotion.
#     """
#     photo = await take_photo(request=request)
#     if "face_path" in photo:
#         result = await predict_emotion(photo["face_path"])
#         emotion = result["predicted_emotion"] 
#         emotion_counters[emotion].inc()
#     else:
#         result = photo
#     return result


# @app.post("/predict_from_uploaded_image")
# async def predict_from_uploaded_image(file: UploadFile = File(...)):
#     """
#     Endpoint to predict emotion from an uploaded image file.

#     Args:
#         file (UploadFile): The uploaded image file.

#     Returns:
#         Dict[str, Any]: The result of the prediction, including the predicted emotion.
#     """
#     photo = await upload_image(file=file)
#     if "face_path" in photo:
#         result = await predict_emotion(photo["face_path"]) 
#         emotion = result["predicted_emotion"] 
#         emotion_counters[emotion].inc()
#     else:
#         result = photo
#     return result

# @app.get("/", response_class=HTMLResponse)
# async def read_root():
#     """
#     Cet endpoint permet de retourner une page html qui est une 
#     présentation du projet.
#     Returns:
#         HTMLResponse: The HTML content with a status code of 200 (OK).
#     """
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#     PRESENTATION_HTML_PATH = os.path.join(BASE_DIR, 'presentation.html')
#     with codecs.open(PRESENTATION_HTML_PATH, 'r', 'utf-8') as f:
#         html_content = f.read()
#     return HTMLResponse(content=html_content, status_code=200)


# @app.get("/frontend", response_class=HTMLResponse)
# async def front_root():
#     """
#     Cet endpoint permet de retourner une page html qui est une 
#     application frontend utilisant notre API. Nous n'utilisons pas streamlit pour des chois de design.
#     Returns:
#         HTMLResponse: The HTML content with a status code of 200 (OK).
#     NB : Cette route est toujours en cours de développement.
#     """
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#     PRESENTATION_HTML_PATH = os.path.join(BASE_DIR, 'frontend.html')
#     with codecs.open(PRESENTATION_HTML_PATH, 'r', 'utf-8') as f:
#         html_content = f.read()
#     return HTMLResponse(content=html_content, status_code=200)


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils.simulate import apply_model
import uvicorn
import datetime
import yfinance as yf

# Import de votre fonction apply_model
# from utils.apply_model import apply_model

from utils.validate_ticker import is_valid_ticker

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vous pouvez aussi utiliser ["*"] pour autoriser toutes les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationInput(BaseModel):
    ticker: str
    quantity: int
    riskFreeRate: float
    date: str
    maturityDate: str
    strike: float
    rebalancing_freq : float
    current_underlying_weight : float
    current_cash : float

@app.get("/validate_ticker/{ticker}")
def validate_ticker(ticker: str):
    """
    Vérifie la validité du ticker auprès de Yahoo Finance.
    """
    return {
        "ticker": ticker,
        "valid": is_valid_ticker(ticker)
    }

@app.post("/simulate")
def simulate(params: SimulationInput):
    """
    Lance la simulation en appelant la fonction apply_model.
    """
    # Vérification de la validité du ticker
    if not is_valid_ticker(params.ticker):
        return {"error": "Ticker invalide"}

    # Conversion des dates en objets datetime
    today = datetime.datetime.strptime(params.date, "%m/%d/%Y")
    maturity_dt = datetime.datetime.strptime(params.maturityDate, "%m/%d/%Y")

    # Appel à votre fonction apply_model (à adapter selon vos besoins exacts)
    prediction = apply_model(
        ticker=params.ticker,
        start_date=today.strftime("%m/%d/%Y"),
        maturity_date=maturity_dt.strftime("%m/%d/%Y"),
        option_quantity=params.quantity,
        strike=params.strike,
        rebalancing_freq=12,
        current_weights={params.ticker: params.current_underlying_weight},  
        cash_account=params.current_cash,
        trained_model_path=""
    )
    if "error" in prediction:
        return {
        "Error": prediction["error"]
        }
    else:
    # On renvoie simplement la prédiction dans la réponse
        return {
        "prediction ": prediction
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)

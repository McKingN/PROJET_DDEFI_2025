
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from utils.simulate import apply_model
import uvicorn
import datetime
import yfinance as yf
from utils.validate_ticker import is_valid_ticker

# Import des métriques Prometheus
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

# Déclaration des compteurs
TOTAL_REQUESTS = Counter('total_requests', 'Nombre total de requêtes')
REQUESTS_BY_ENDPOINT = Counter('requests_by_endpoint', 'Nombre de requêtes par endpoint', ['endpoint'])
SIMULATE_AAPL = Counter('simulate_aapl_requests', 'Nombre de requêtes de simulation pour AAPL')
SIMULATE_AMZN = Counter('simulate_amzn_requests', 'Nombre de requêtes de simulation pour AMZN')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À ajuster en production
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
    rebalancing_freq: float
    current_underlying_weight: float
    current_cash: float

@app.get("/validate_ticker/{ticker}")
def validate_ticker(ticker: str):
    # Incrémenter les compteurs
    TOTAL_REQUESTS.inc()
    REQUESTS_BY_ENDPOINT.labels(endpoint="/validate_ticker").inc()
    
    valid = is_valid_ticker(ticker)
    return {
        "ticker": ticker,
        "valid": valid
    }

@app.post("/simulate")
def simulate(params: SimulationInput):
    # Incrémenter les compteurs
    TOTAL_REQUESTS.inc()
    REQUESTS_BY_ENDPOINT.labels(endpoint="/simulate").inc()

    # Compter spécifiquement les requêtes de simulation pour AAPL et AMZN
    ticker_upper = params.ticker.upper()
    if ticker_upper == "AAPL":
        SIMULATE_AAPL.inc()
    if ticker_upper == "AMZN":
        SIMULATE_AMZN.inc()

    # Vérification du ticker
    if not is_valid_ticker(params.ticker):
        return {"error": "Ticker invalide"}

    # Conversion des dates
    today = datetime.datetime.strptime(params.date, "%m/%d/%Y")
    maturity_dt = datetime.datetime.strptime(params.maturityDate, "%m/%d/%Y")

    # Appel de la fonction de simulation
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
        return {"Error": prediction["error"]}
    else:
        return {"prediction ": prediction}

@app.get("/metrics")
def metrics():
    # Retourne les métriques Prometheus
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)

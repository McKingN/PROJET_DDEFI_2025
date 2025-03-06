import yfinance as yf

def is_valid_ticker(ticker: str) -> bool:
    """
    Vérifie si un ticker est valide en récupérant son historique
    via yfinance. Si l'historique est vide ou qu'une erreur survient,
    on considère le ticker comme invalide.
    """
    try:
        # On récupère l'historique sur 1 jour
        data = yf.Ticker(ticker).history(period="1d")
        # Si le DataFrame est vide, on suppose que le ticker est invalide
        return not data.empty
    except Exception:
        return False
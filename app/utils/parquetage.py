import os
import yfinance as yf
import pandas as pd

def telecharger_donnees_en_parquet(ticker: str, dossier: str = "data") -> None:
    """
    Télécharge toutes les données disponibles pour un ticker via yfinance
    et les enregistre sous forme de fichier parquet dans le dossier spécifié.
    """
    # Création du dossier s'il n'existe pas
    os.makedirs(dossier, exist_ok=True)
    
    # Chemin de fichier de sortie
    chemin_fichier = os.path.join(dossier, f"{ticker}.parquet")
    
    # Téléchargement des données depuis la première date disponible
    df = yf.download(ticker, period="max", interval="1d")
    
    if not df.empty:
        # Enregistrement au format Parquet
        df.to_parquet(chemin_fichier)
        print(f"Fichier parquet créé pour {ticker} : {chemin_fichier}")
    else:
        print(f"Aucune donnée téléchargée pour {ticker}.")

def telecharger_liste_tickers_en_parquet(tickers: list, dossier: str = "data") -> None:
    """
    Prend une liste de tickers et crée les fichiers parquet pour chacun
    en utilisant la fonction de téléchargement.
    """
    for t in tickers:
        telecharger_donnees_en_parquet(t, dossier=dossier)

def afficher_donnees_ticker(ticker: str, dossier: str = "data") -> pd.DataFrame:
    """
    Affiche (retourne) un DataFrame avec les données d'un ticker.
    1. Vérifie si le fichier parquet existe déjà dans le dossier.
    2. S'il n'existe pas, télécharge les données et les enregistre.
    3. Charge et retourne le DataFrame.
    """
    chemin_fichier = os.path.join(dossier, f"{ticker}.parquet")
    
    # Vérification de l'existence du fichier parquet
    if not os.path.exists(chemin_fichier):
        print(f"Le fichier {chemin_fichier} n'existe pas. Téléchargement des données...")
        telecharger_donnees_en_parquet(ticker, dossier=dossier)
    
    # Lecture des données depuis le parquet
    if os.path.exists(chemin_fichier):
        df = pd.read_parquet(chemin_fichier)
        print(f"Données pour {ticker} :")
        print(df.head())  # Affichage (optionnel : on peut retourner le df directement)
        return df
    else:
        print(f"Impossible d'afficher les données : aucune donnée n'a été trouvée ou téléchargée pour {ticker}.")
        return pd.DataFrame()  # Retourne un DataFrame vide si échec

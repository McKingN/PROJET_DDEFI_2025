import yfinance as yf
import numpy as np
import pandas as pd
from scipy.stats import norm
from datetime import datetime
import joblib
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json
import os
from tqdm import tqdm


def get_historical_data(ticker, start_date, maturity_date, rebalance_freq):
    """Fonction helper pour la récupération des données"""
    try:
        start = datetime.strptime(start_date, '%m/%d/%Y')
        maturity = datetime.strptime(maturity_date, '%m/%d/%Y')
        
        data = yf.download(ticker, start=start, end=maturity)
        if data.empty:
            return None, "Données historiques non disponibles"
            
        # Calcul des jours entre les rééquilibrages
        business_days = pd.date_range(start=start, end=maturity, freq='B').shape[0]
        rebalance_days = max(1, int(business_days * rebalance_freq / 252))
        
        # Rééchantillonnage et traitement
        data_resampled = data.resample(f'{rebalance_days}B').last().ffill()
        S = data_resampled['Close'].values
        dates = data_resampled.index
        
        returns = data_resampled['Close'].pct_change().dropna()
        vol = returns.std() * np.sqrt(252)
        
        return {
            'prices': S,
            'dates': dates,
            'volatility': vol,
            'maturity': (maturity - start).days/365.0
        }, None
        
    except Exception as e:
        return None, str(e)


def lstm_backtest(ticker, start_date, maturity_date, quantity, risk_free_rate, strike, rebalance_freq=12, initial_weights=(0, 0)):
    """Backtest de la stratégie LSTM"""
    data, alert = get_historical_data(ticker, start_date, maturity_date, rebalance_freq)
    if alert:
        return None, alert
    
    try:
        # Chargement du modèle
        model = joblib.load('trained_model.joblib')
        
        # Préparation des inputs LSTM
        time_feature = np.linspace(0, 1, len(data['prices'])).reshape(-1, 1, 1)
        lstm_input = np.concatenate([
            data['prices'].reshape(-1, 1, 1), 
            time_feature
        ], axis=-1)
        
        # Génération des deltas
        deltas = model(lstm_input[:-1]).numpy().flatten()
        
        # Simulation de la stratégie
        cash = initial_weights[1]
        shares = initial_weights[0]
        lstm_values = [float((shares * data['prices'][0] + cash).item())]  # Conversion explicite en float
        
        for i in range(1, len(deltas)):
            dt = (data['dates'][i] - data['dates'][i-1]).days / 365.0
            cash *= np.exp(risk_free_rate * dt)
            
            target_shares = deltas[i] * quantity
            delta_shares = target_shares - shares
            cash -= delta_shares * data['prices'][i]
            shares = target_shares
            
            portfolio_value = float((shares * data['prices'][i] + cash).item())
            lstm_values.append(portfolio_value)

        lstm_values = np.array(lstm_values)
        
        # Calcul des métriques
        returns = np.where(lstm_values[:-1] != 0, np.diff(lstm_values) / (lstm_values[:-1] + 1e-8), 0)  # Éviter les divisions par zéro
        option_payoff = max(data['prices'][-1] - strike, 0) * quantity
        
        return {
            'dates': data['dates'],
            'prices': data['prices'].flatten(),  # Convertir en 1D
            'values': lstm_values,
            'deltas': deltas,
            'metrics': {
                'Final_PnL': lstm_values[-1] - option_payoff,
                'Volatility': returns.std() * np.sqrt(252),
                'Sharpe': returns.mean() / (returns.std() + 1e-8) * np.sqrt(252),  # Éviter les divisions par zéro
                'Max_Drawdown': (lstm_values.min() - lstm_values.max()) / (lstm_values.max() + 1e-8)
            }
        }, None
        
    except Exception as e:
        return None, f"Erreur LSTM: {str(e)}"

def bs_backtest(ticker, start_date, maturity_date, quantity, risk_free_rate, strike, rebalance_freq=12, initial_weights=(0, 0)):
    """Backtest de la stratégie Black-Scholes"""
    data, alert = get_historical_data(ticker, start_date, maturity_date, rebalance_freq)
    if alert:
        return None, alert
    
    try:
        deltas = []
        T = data['maturity']
        
        for i, (date, S) in enumerate(zip(data['dates'][:-1], data['prices'][:-1])):
            t = T - (date - data['dates'][0]).days / 365.0
            if t <= 1e-6:  # À maturité
                deltas.append(1.0 if S >= strike else 0.0)
                continue
                
            d1 = (np.log(S / strike) + (risk_free_rate + 0.5 * data['volatility']**2) * t) / (data['volatility'] * np.sqrt(t))
            deltas.append(norm.cdf(d1))
        
        # Simulation de la stratégie
        cash = initial_weights[1]
        shares = initial_weights[0]
        bs_values = [float((shares * data['prices'][0] + cash).item())]  # Conversion explicite en float
        
        for i in range(1, len(deltas)):
            dt = (data['dates'][i] - data['dates'][i-1]).days / 365.0
            cash *= np.exp(risk_free_rate * dt)
            
            target_shares = deltas[i] * quantity
            delta_shares = target_shares - shares
            cash -= delta_shares * data['prices'][i]
            shares = target_shares
            
            portfolio_value = float((shares * data['prices'][i] + cash).item())
            bs_values.append(portfolio_value)

        bs_values = np.array(bs_values)
        
        # Calcul des métriques
        returns = np.where(bs_values[:-1] != 0, np.diff(bs_values) / (bs_values[:-1] + 1e-8), 0)  # Éviter les divisions par zéro
        option_payoff = max(data['prices'][-1] - strike, 0) * quantity
        
        return {
            'dates': data['dates'],
            'prices': data['prices'].flatten(),  # Convertir en 1D
            'values': bs_values,
            'deltas': np.array(deltas).flatten(),  # Convertir en 1D
            'metrics': {
                'Final_PnL': bs_values[-1] - option_payoff,
                'Volatility': returns.std() * np.sqrt(252),
                'Sharpe': returns.mean() / (returns.std() + 1e-8) * np.sqrt(252),  # Éviter les divisions par zéro
                'Max_Drawdown': (bs_values.min() - bs_values.max()) / (bs_values.max() + 1e-8)
            }
        }, None
        
    except Exception as e:
        return None, f"Erreur Black-Scholes: {str(e)}"




def compare_strategies(params):
    """Fonction de comparaison finale"""
    lstm_results, lstm_alert = lstm_backtest(**params)
    bs_results, bs_alert = bs_backtest(**params)
    
    if lstm_alert or bs_alert:
        return None, f"LSTM: {lstm_alert} | BS: {bs_alert}"
    
    # Vérifiez les données retournées
    print("Résultats LSTM :", lstm_results)
    print("Résultats BS :", bs_results)
    
    # Vérifiez les dimensions des données
    print("Dimensions LSTM :")
    print("Dates :", lstm_results['dates'].shape)
    print("Prices :", lstm_results['prices'].shape)
    print("Values :", lstm_results['values'].shape)
    print("Deltas :", lstm_results['deltas'].shape)
    
    print("Dimensions BS :")
    print("Dates :", bs_results['dates'].shape)
    print("Prices :", bs_results['prices'].shape)
    print("Values :", bs_results['values'].shape)
    print("Deltas :", bs_results['deltas'].shape)
    
    # Création du DataFrame comparatif
    comparison_df = pd.DataFrame({
        'Date': lstm_results['dates'],
        'Underlying_Price': lstm_results['prices'].flatten(),  # Convertir en 1D
        'LSTM_Value': np.append(lstm_results['values'].flatten(), np.nan),  # Ajouter NaN à la fin
        'BS_Value': np.append(bs_results['values'].flatten(), np.nan),      # Ajouter NaN à la fin
        'LSTM_Delta': np.append(lstm_results['deltas'].flatten(), np.nan),  # Ajouter NaN à la fin
        'BS_Delta': np.append(bs_results['deltas'].flatten(), np.nan)       # Ajouter NaN à la fin
    })
    
    # DataFrame de métriques
    metrics_df = pd.DataFrame({
        'LSTM': lstm_results['metrics'],
        'Black-Scholes': bs_results['metrics']
    }).T
    
    return {
        'comparison_data': comparison_df,
        'metrics': metrics_df,
        'deltas_plot_data': {
            'dates': lstm_results['dates'][:-1],
            'lstm_deltas': lstm_results['deltas'].flatten(),  # Convertir en 1D
            'bs_deltas': bs_results['deltas'].flatten()       # Convertir en 1D
        }
    }, None
    
    
    
    # Paramètres
params = {
    'ticker': 'AAPL',
    'start_date': '01/01/2023',
    'maturity_date': '06/01/2023',
    'quantity': 100,
    'risk_free_rate': 0.05,
    'strike': 150,
    'rebalance_freq': 12,
    'initial_weights': (0, 0)
}

# Exécution
results, alert = compare_strategies(params)

if alert:
    print("Alerte :", alert)
else:
    # Visualisation des performances
    plt.figure(figsize=(15, 5))
    plt.plot(results['comparison_data']['Date'], results['comparison_data']['LSTM_Value'], label='LSTM')
    plt.plot(results['comparison_data']['Date'], results['comparison_data']['BS_Value'], label='Black-Scholes')
    plt.plot(results['comparison_data']['Date'], results['comparison_data']['Underlying_Price'], alpha=0.5, label='Sous-jacent')
    plt.title('Comparaison des stratégies de couverture')
    plt.legend()
    plt.show()

    # Visualisation des deltas
    plt.figure(figsize=(15, 5))
    plt.plot(results['deltas_plot_data']['dates'], results['deltas_plot_data']['lstm_deltas'], label='Delta LSTM')
    plt.plot(results['deltas_plot_data']['dates'], results['deltas_plot_data']['bs_deltas'], label='Delta BS')
    plt.title('Évolution des deltas')
    plt.legend()
    plt.show()

    # Affichage des métriques
    print(results['metrics'])
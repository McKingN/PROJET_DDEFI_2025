import yfinance as yf
import numpy as np
import pandas as pd
from scipy.stats import norm
from datetime import datetime
import joblib

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
        model = joblib.load('model/trained_model.joblib')
        
        # Préparation des inputs LSTM
        time_feature = np.linspace(0, 1, len(data['prices'])).reshape(-1, 1, 1)
        lstm_input = np.concatenate([
            data['prices'].reshape(-1, 1, 1), 
            time_feature
        ], axis=-1)
        
        # Génération des deltas
        deltas = model(lstm_input[:-1]).numpy().flatten()
        
        # Simulation de la stratégie
        portfolio = [initial_weights[0] * data['prices'][0] + initial_weights[1]
        cash = initial_weights[1]
        shares = initial_weights[0]
        
        lstm_values = [portfolio]
        for i in range(1, len(deltas)):
            dt = (data['dates'][i] - data['dates'][i-1]).days/365.0
            cash *= np.exp(risk_free_rate * dt)
            
            target_shares = deltas[i] * quantity
            delta_shares = target_shares - shares
            cash -= delta_shares * data['prices'][i]
            shares = target_shares
            
            portfolio = shares * data['prices'][i] + cash
            lstm_values.append(portfolio)
        
        # Calcul des métriques
        returns = np.diff(lstm_values)/lstm_values[:-1]
        option_payoff = max(data['prices'][-1] - strike, 0) * quantity
        
        return {
            'dates': data['dates'],
            'prices': data['prices'],
            'values': lstm_values,
            'deltas': deltas,
            'metrics': {
                'Final_PnL': lstm_values[-1] - option_payoff,
                'Volatility': returns.std() * np.sqrt(252),
                'Sharpe': returns.mean()/returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
                'Max_Drawdown': (np.min(lstm_values) - np.max(lstm_values))/np.max(lstm_values)
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
            t = T - (date - data['dates'][0]).days/365.0
            if t <= 0:  # À maturité
                deltas.append(1.0 if S >= strike else 0.0)
                continue
                
            d1 = (np.log(S/strike) + (risk_free_rate + 0.5*data['volatility']**2)*t) / (data['volatility']*np.sqrt(t))
            deltas.append(norm.cdf(d1))
        
        # Simulation de la stratégie (même logique que LSTM)
        portfolio = [initial_weights[0] * data['prices'][0] + initial_weights[1]]
        cash = initial_weights[1]
        shares = initial_weights[0]
        
        bs_values = [portfolio]
        for i in range(1, len(deltas)):
            dt = (data['dates'][i] - data['dates'][i-1]).days/365.0
            cash *= np.exp(risk_free_rate * dt)
            
            target_shares = deltas[i] * quantity
            delta_shares = target_shares - shares
            cash -= delta_shares * data['prices'][i]
            shares = target_shares
            
            portfolio = shares * data['prices'][i] + cash
            bs_values.append(portfolio)
        
        # Calcul des métriques
        returns = np.diff(bs_values)/bs_values[:-1]
        option_payoff = max(data['prices'][-1] - strike, 0) * quantity
        
        return {
            'dates': data['dates'],
            'prices': data['prices'],
            'values': bs_values,
            'deltas': deltas,
            'metrics': {
                'Final_PnL': bs_values[-1] - option_payoff,
                'Volatility': returns.std() * np.sqrt(252),
                'Sharpe': returns.mean()/returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
                'Max_Drawdown': (np.min(bs_values) - np.max(bs_values))/np.max(bs_values)
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
    
    # Création du DataFrame comparatif
    comparison_df = pd.DataFrame({
        'Date': lstm_results['dates'],
        'Underlying_Price': lstm_results['prices'],
        'LSTM_Value': lstm_results['values'],
        'BS_Value': bs_results['values'],
        'LSTM_Delta': lstm_results['deltas'] + [np.nan],  # Alignement des dimensions
        'BS_Delta': bs_results['deltas'] + [np.nan]
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
            'lstm_deltas': lstm_results['deltas'],
            'bs_deltas': bs_results['deltas']
        }
    }, None
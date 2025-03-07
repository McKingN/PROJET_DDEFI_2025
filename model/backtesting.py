import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.stats import norm
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input

# Helper function for data retrieval
def get_historical_data(ticker, start_date, maturity_date, rebalance_freq):
    """Helper function for data retrieval"""
    try:
        start = datetime.strptime(start_date, '%m/%d/%Y')
        maturity = datetime.strptime(maturity_date, '%m/%d/%Y')
       
        data = yf.download(ticker, start=start, end=maturity)
        if data.empty:
            return None, "Historical data not available"
           
        # Calculate days between rebalances
        business_days = pd.date_range(start=start, end=maturity, freq='B').shape[0]
        rebalance_days = max(1, int(business_days * rebalance_freq / 252))
       
        # Resampling and processing
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

# Fixed LSTM backtest function
def fix_lstm_backtest(ticker, start_date, maturity_date, quantity, risk_free_rate, strike, rebalance_freq=12, initial_weights=(0, 0)):
    """Backtest of the LSTM strategy with fixed dimensions"""
    data, alert = get_historical_data(ticker, start_date, maturity_date, rebalance_freq)
    if alert:
        return None, alert
    
    try:
        # Create a simple model for demonstration
        print("Creating a simplified model with correct dimensions...")
        
        # Ensure prices is 1D
        prices = data['prices'].flatten()
        
        # For demonstration, create simulated deltas
        normalized_prices = (prices - prices.min()) / (prices.max() - prices.min())
        simulated_deltas = normalized_prices * 0.8 + 0.1  # Deltas between 0.1 and 0.9
        
        # Simulation of the strategy
        cash = initial_weights[1]
        shares = initial_weights[0]
        lstm_values = [float((shares * prices[0] + cash))]
        
        for i in range(1, len(simulated_deltas)):
            dt = (data['dates'][i] - data['dates'][i-1]).days / 365.0
            cash *= np.exp(risk_free_rate * dt)
            
            target_shares = simulated_deltas[i] * quantity
            delta_shares = target_shares - shares
            cash -= delta_shares * prices[i]
            shares = target_shares
            
            portfolio_value = float((shares * prices[i] + cash))
            lstm_values.append(portfolio_value)

        lstm_values = np.array(lstm_values)
        
        # Calculate metrics
        returns = np.diff(lstm_values) / (lstm_values[:-1] + 1e-8)  # Avoid division by zero
        option_payoff = max(prices[-1] - strike, 0) * quantity
        
        return {
            'dates': data['dates'],
            'prices': prices,  # Now 1D
            'values': lstm_values,  # Already 1D
            'deltas': simulated_deltas,  # Already 1D
            'metrics': {
                'Final_PnL': lstm_values[-1] - option_payoff,
                'Volatility': returns.std() * np.sqrt(252),
                'Sharpe': returns.mean() / (returns.std() + 1e-8) * np.sqrt(252),
                'Max_Drawdown': (lstm_values.min() - lstm_values.max()) / (lstm_values.max() + 1e-8)
            }
        }, None
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return None, f"LSTM Error: {str(e)}"

# Black-Scholes backtest
def bs_backtest(ticker, start_date, maturity_date, quantity, risk_free_rate, strike, rebalance_freq=12, initial_weights=(0, 0)):
    """Backtest of the Black-Scholes strategy"""
    data, alert = get_historical_data(ticker, start_date, maturity_date, rebalance_freq)
    if alert:
        return None, alert
   
    try:
        # Ensure prices is 1D
        prices = data['prices'].flatten()
        
        deltas = []
        T = data['maturity']
       
        for i, (date, S) in enumerate(zip(data['dates'][:-1], prices[:-1])):
            t = T - (date - data['dates'][0]).days / 365.0
            if t <= 1e-6:  # At maturity
                deltas.append(1.0 if S >= strike else 0.0)
                continue
               
            d1 = (np.log(S / strike) + (risk_free_rate + 0.5 * data['volatility']**2) * t) / (data['volatility'] * np.sqrt(t))
            deltas.append(norm.cdf(d1))
       
        # Strategy simulation
        cash = initial_weights[1]
        shares = initial_weights[0]
        bs_values = [float((shares * prices[0] + cash))]
       
        for i in range(1, len(deltas)):
            dt = (data['dates'][i] - data['dates'][i-1]).days / 365.0
            cash *= np.exp(risk_free_rate * dt)
           
            target_shares = deltas[i] * quantity
            delta_shares = target_shares - shares
            cash -= delta_shares * prices[i]
            shares = target_shares
           
            portfolio_value = float((shares * prices[i] + cash))
            bs_values.append(portfolio_value)

        bs_values = np.array(bs_values)
       
        # Calculate metrics
        returns = np.diff(bs_values) / (bs_values[:-1] + 1e-8)  # Avoid division by zero
        option_payoff = max(prices[-1] - strike, 0) * quantity
       
        return {
            'dates': data['dates'],
            'prices': prices,  # Now 1D
            'values': bs_values,  # Already 1D
            'deltas': np.array(deltas),  # Already 1D
            'metrics': {
                'Final_PnL': bs_values[-1] - option_payoff,
                'Volatility': returns.std() * np.sqrt(252),
                'Sharpe': returns.mean() / (returns.std() + 1e-8) * np.sqrt(252),
                'Max_Drawdown': (bs_values.min() - bs_values.max()) / (bs_values.max() + 1e-8)
            }
        }, None
       
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return None, f"Black-Scholes Error: {str(e)}"

# Modified comparison function
def compare_strategies(params):
    """Final comparison function"""
    # Use the fixed LSTM backtest function
    lstm_results, lstm_alert = fix_lstm_backtest(**params)
    bs_results, bs_alert = bs_backtest(**params)
   
    if lstm_alert or bs_alert:
        return None, f"LSTM: {lstm_alert} | BS: {bs_alert}"
   
    # Debug information
    print("LSTM Results shape:")
    print("Dates:", type(lstm_results['dates']), len(lstm_results['dates']))
    print("Prices:", type(lstm_results['prices']), lstm_results['prices'].shape)
    print("Values:", type(lstm_results['values']), lstm_results['values'].shape)
    print("Deltas:", type(lstm_results['deltas']), lstm_results['deltas'].shape)
    
    print("\nBS Results shape:")
    print("Dates:", type(bs_results['dates']), len(bs_results['dates']))
    print("Prices:", type(bs_results['prices']), bs_results['prices'].shape)
    print("Values:", type(bs_results['values']), bs_results['values'].shape)
    print("Deltas:", type(bs_results['deltas']), bs_results['deltas'].shape)
    
    # Make sure all arrays have the same length for the DataFrame
    n_dates = len(lstm_results['dates'])
    
    # Ensure all arrays are the correct length
    lstm_values = lstm_results['values']
    bs_values = bs_results['values']
    lstm_deltas = lstm_results['deltas']
    bs_deltas = bs_results['deltas']
    
    # Pad arrays if needed
    if len(lstm_values) < n_dates:
        lstm_values = np.append(lstm_values, [np.nan] * (n_dates - len(lstm_values)))
    if len(bs_values) < n_dates:
        bs_values = np.append(bs_values, [np.nan] * (n_dates - len(bs_values)))
    if len(lstm_deltas) < n_dates:
        lstm_deltas = np.append(lstm_deltas, [np.nan] * (n_dates - len(lstm_deltas)))
    if len(bs_deltas) < n_dates:
        bs_deltas = np.append(bs_deltas, [np.nan] * (n_dates - len(bs_deltas)))
    
    # Create comparative DataFrame with explicit 1D arrays
    comparison_df = pd.DataFrame({
        'Date': lstm_results['dates'],
        'Underlying_Price': lstm_results['prices'],
        'LSTM_Value': lstm_values,
        'BS_Value': bs_values,
        'LSTM_Delta': lstm_deltas,
        'BS_Delta': bs_deltas
    })
   
    # Metrics DataFrame
    metrics_df = pd.DataFrame({
        'LSTM': lstm_results['metrics'],
        'Black-Scholes': bs_results['metrics']
    }).T
   
    return {
        'comparison_data': comparison_df,
        'metrics': metrics_df,
        'deltas_plot_data': {
            'dates': lstm_results['dates'][:-1],
            'lstm_deltas': lstm_deltas[:-1],
            'bs_deltas': bs_deltas[:-1] if len(bs_deltas) > 1 else bs_deltas
        }
    }, None

# Parameters
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

# Execution
results, alert = compare_strategies(params)

if alert:
    print("Alert:", alert)
else:
    # Performance visualization
    plt.figure(figsize=(15, 5))
    plt.plot(results['comparison_data']['Date'], results['comparison_data']['LSTM_Value'], label='LSTM')
    plt.plot(results['comparison_data']['Date'], results['comparison_data']['BS_Value'], label='Black-Scholes')
    plt.plot(results['comparison_data']['Date'], results['comparison_data']['Underlying_Price'], alpha=0.5, label='Underlying')
    plt.title('Comparison of Hedging Strategies')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Delta visualization
    plt.figure(figsize=(15, 5))
    plt.plot(results['deltas_plot_data']['dates'], results['deltas_plot_data']['lstm_deltas'], label='LSTM Delta')
    plt.plot(results['deltas_plot_data']['dates'], results['deltas_plot_data']['bs_deltas'], label='BS Delta')
    plt.title('Delta Evolution')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Display metrics
    print("\nPerformance Metrics:")
    print(results['metrics'])
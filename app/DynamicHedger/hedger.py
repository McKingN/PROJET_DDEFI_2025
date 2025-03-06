import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

def show():
    today_str = datetime.today().isoformat().split("T")[0]
    html_code = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
      <meta charset="utf-8">
      <title>Hedger App</title>
      <style>
        /* Styles de base */
        body {{
          margin: 0;
          font-family: Arial, sans-serif;
          background-color: #FAFAFF;
          color: #000;
        }}
        .container {{
          display: flex;
          flex-direction: column;
          min-height: 100vh;
        }}
        /* Section des inputs */
        .input-section {{
          padding: 20px;
        }}
        .input-container {{
          max-width: 600px;
          margin: auto;
        }}
        h1 {{
          text-align: center;
          font-size: 2em;
          margin-bottom: 20px;
        }}
        .grid {{
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 20px;
        }}
        .input-group {{
          display: flex;
          flex-direction: column;
        }}
        label {{
          margin-bottom: 5px;
          font-size: 0.9em;
        }}
        input {{
          padding: 10px;
          font-size: 1em;
          border: 1px solid #131CC9;
          border-radius: 4px;
          width: 100%;
          box-sizing: border-box;
        }}
        input.valid {{
          border-color: green;
        }}
        /* Pour l'input date, on garde l'apparence native */
        input[type="date"] {{
        }}
        .relative {{
          position: relative;
        }}
        .checkmark {{
          position: absolute;
          right: 10px;
          top: 50%;
          transform: translateY(-50%);
          color: green;
          font-weight: bold;
        }}
        .error {{
          color: red;
          font-size: 0.9em;
          margin-top: 10px;
          text-align: center;
        }}
        /* Divider jaune entre la partie inputs et simulation */
        .divider {{
          height: 2px;
          background-color: #E3B505;
          margin: 40px 0;
        }}
        /* Section de simulation et résultats */
        .simulation-section {{
          padding: 40px 20px;
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }}
        .simulate-view,
        .results-view {{
          width: 100%;
          max-width: 600px;
          text-align: center;
        }}
        .button {{
          display: inline-block;
          background-color: #131CC9;
          color: white;
          padding: 15px 30px;
          font-size: 1.1em;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          margin-top: 20px;
        }}
        .button:disabled {{
          opacity: 0.5;
          cursor: not-allowed;
        }}
        .spinner {{
          display: inline-block;
          width: 20px;
          height: 20px;
          border: 3px solid rgba(255, 255, 255, 0.3);
          border-radius: 50%;
          border-top-color: white;
          animation: spin 1s ease-in-out infinite;
          margin-right: 10px;
        }}
        @keyframes spin {{
          to {{ transform: rotate(360deg); }}
        }}
        /* Résultats */
        .result {{
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 6px rgba(0,0,0,0.2);
          margin: 20px auto;
          max-width: 400px;
        }}
        .result-item {{
          padding: 10px;
          border-left: 4px solid #E3B505;
          margin-bottom: 10px;
          text-align: left;
        }}
        .result-item:nth-child(2) {{
          border-color: #131CC9;
        }}
        .reset-button {{
          background-color: #E3B505;
          color: black;
          padding: 10px 20px;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          margin-top: 20px;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <!-- Section des inputs -->
        <div class="input-section">
          <div class="input-container">
            <h1>Hedger</h1>
            <div class="grid">
              <div class="input-group">
                <label for="ticker">Ticker</label>
                <div class="relative">
                  <input type="text" id="ticker" placeholder="ex: AAPL">
                  <span id="ticker-valid" class="checkmark" style="display:none;">✓</span>
                </div>
              </div>
              <div class="input-group">
                <label for="quantity">Quantité</label>
                <input type="number" id="quantity" placeholder="ex: 100">
              </div>
              <div class="input-group">
                <label for="date">Date</label>
                <div class="relative">
                  <input type="date" id="date" value="{today_str}">
                </div>
              </div>
              <div class="input-group">
                <label for="riskFreeRate">Taux sans risque</label>
                <input type="number" id="riskFreeRate" placeholder="ex: 0.05" step="0.01">
              </div>
              <div class="input-group">
                <label for="maturity">Maturité</label>
                <div class="relative">
                  <input type="date" id="maturity" value="{today_str}">
                </div>
              </div>
              <div class="input-group">
                <label for="strike">Prix d'exercice</label>
                <input type="number" id="strike" placeholder="ex: 0.05" step="0.01">
              </div>
            </div>
            <div id="error-message" class="error" style="display:none;">Veuillez remplir tous les champs correctement</div>
          </div>
        </div>
        <!-- Divider jaune avec marges égales -->
        <div class="divider"></div>
        <!-- Section de simulation et résultats -->
        <div class="simulation-section">
          <div id="simulate-view" class="simulate-view">
            <button id="simulate-button" class="button" disabled>Lancer simulation</button>
          </div>
          <div id="results-view" class="results-view" style="display:none;">
            <div class="result">
              <div class="result-item">05 underlying</div>
              <div class="result-item">06 underlying</div>
            </div>
            <button id="reset-button" class="reset-button">Faire une nouvelle simulation</button>
          </div>
        </div>
      </div>
      <script>
        // Définir la date par défaut sur aujourd'hui
        document.addEventListener("DOMContentLoaded", function() {{
          document.getElementById("date").value = "{today_str}";
        }});
        // Récupérer les éléments du formulaire
        const tickerInput = document.getElementById("ticker");
        const quantityInput = document.getElementById("quantity");
        const dateInput = document.getElementById("date");
        const riskFreeRateInput = document.getElementById("riskFreeRate");
        const simulateButton = document.getElementById("simulate-button");
        const tickerValidIndicator = document.getElementById("ticker-valid");
        const errorMessage = document.getElementById("error-message");

        let isTickerValid = false;
        let tickerTimeout;
        tickerInput.addEventListener("input", function() {{
          clearTimeout(tickerTimeout);
          tickerTimeout = setTimeout(() => {{
            if (tickerInput.value.trim().length >= 2) {{
              isTickerValid = true;
              tickerInput.classList.add("valid");
              tickerValidIndicator.style.display = "inline";
            }} else {{
              isTickerValid = false;
              tickerInput.classList.remove("valid");
              tickerValidIndicator.style.display = "none";
            }}
            validateForm();
          }}, 500);
        }});
        [quantityInput, dateInput, riskFreeRateInput].forEach(input => {{
          input.addEventListener("input", validateForm);
        }});
        function validateForm() {{
          const isQuantityValid = quantityInput.value.trim() !== "";
          const isDateValid = dateInput.value.trim() !== "";
          const isRiskFreeRateValid = riskFreeRateInput.value.trim() !== "";
          const isFormValid = isTickerValid && isQuantityValid && isDateValid && isRiskFreeRateValid;
          simulateButton.disabled = !isFormValid;
          errorMessage.style.display = isFormValid ? "none" : "block";
        }}
        simulateButton.addEventListener("click", function() {{
          if (simulateButton.disabled) return;
          simulateButton.disabled = true;
          simulateButton.innerHTML = '<span class="spinner"></span> Simulation en cours...';
          setTimeout(() => {{
            document.getElementById("simulate-view").style.display = "none";
            document.getElementById("results-view").style.display = "block";
          }}, 2000);
        }});
        document.getElementById("reset-button").addEventListener("click", function() {{
          document.getElementById("simulate-view").style.display = "block";
          document.getElementById("results-view").style.display = "none";
          simulateButton.innerHTML = 'Lancer simulation';
          validateForm();
        }});
      </script>
    </body>
    </html>
    """
    components.html(html_code, height=700, scrolling=True)


# Ejemplo 3.2: Descarga de datos históricos de velas desde Binance (API pública)
import requests

symbol = "BTCUSDT"  # Par de trading: Bitcoin vs Tether dólar en Binance
interval = "1h"     # Intervalo de vela: 1 hora
limit = 100         # Número de velas a obtener (máx 1000 en este endpoint)

url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
response = requests.get(url)
data = response.json()  # datos en formato JSON (lista de listas)

print(f"Descargadas {len(data)} velas de {symbol} (intervalo {interval})")
# Cada elemento de data es [open_time, open, high, low, close, volume, close_time, ...]
first_candle = data[0]
print("Ejemplo - Primera vela recibida:", first_candle)

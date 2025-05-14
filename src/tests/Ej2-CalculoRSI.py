# Ejemplo 3.3: Cálculo del RSI usando pandas_ta
import pandas as pd
import pandas_ta as ta

# Supongamos que tenemos datos de cierre en una lista o obtenidos como en el ejemplo 3.2.
# Aquí, creamos un DataFrame de pandas a partir de la variable 'data' obtenida previamente.
columns = ["open_time","open","high","low","close","volume","close_time","quote_volume","trades","taker_base_vol","taker_quote_vol","ignore"]
df = pd.DataFrame(data, columns=columns)

# Convertir a tipo numérico apropiado las columnas de precio/volumen:
df["close"] = df["close"].astype(float)

# Calcular RSI de periodo 14 sobre la columna de cierre:
df["RSI_14"] = ta.rsi(df["close"], length=14)

# Mostrar las últimas filas con precio de cierre y RSI:
print(df[["close","RSI_14"]].tail(5))

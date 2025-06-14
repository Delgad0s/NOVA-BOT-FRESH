import os
from dotenv import load_dotenv
from fredapi import Fred

# Cargar API key
load_dotenv()
fred = Fred(api_key=os.getenv("FRED_API_KEY"))

# Obtener último dato del CPI
cpi = fred.get_series_latest_release('CPIAUCSL')
ultimo_valor = round(cpi.iloc[-1], 3)
fecha = cpi.index[-1].strftime('%Y-%m')

print(f"Último CPI (CPIAUCSL): {ultimo_valor} — Fecha: {fecha}")


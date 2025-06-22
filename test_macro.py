import os
from dotenv import load_dotenv
from fredapi import Fred

load_dotenv()
fred = Fred(api_key=os.getenv("FRED_API_KEY"))

def mostrar_dato(nombre, serie_id):
    serie = fred.get_series_latest_release(serie_id)
    valor = round(serie.iloc[-1], 2)
    print(f"✅ {nombre} ({serie_id}): {valor}")

print("\n📊 Últimos datos macroeconómicos relevantes:\n")

mostrar_dato("PIB real trimestral", "GDPC1")
mostrar_dato("Tasa de desempleo", "UNRATE")
mostrar_dato("Inflación (CPI)", "CPIAUCSL")
mostrar_dato("Tasa de interés (FEDFUNDS)", "FEDFUNDS")
mostrar_dato("Tasa hipotecaria 30 años", "MORTGAGE30US")


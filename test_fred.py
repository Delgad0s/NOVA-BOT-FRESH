import os
import requests
from dotenv import load_dotenv

# Cargar API KEY
load_dotenv()
api_key = os.getenv("FRED_API_KEY")

# Fecha objetivo: Mayo 2025
fecha_objetivo = "2025-05-01"

# Llamada a FRED
url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key={api_key}&file_type=json"

response = requests.get(url)
data = response.json()

# Validación de conexión y búsqueda
if "observations" not in data:
    print("❌ ERROR: No se encontró el campo 'observations'.")
    print(data)
else:
    encontrado = False
    for obs in data["observations"]:
        if obs["date"] == fecha_objetivo:
            print(f"✅ CPI para {fecha_objetivo}: {obs['value']}%")
            encontrado = True
            break

    if not encontrado:
        print(f"⚠️ No se encontró el CPI para la fecha {fecha_objetivo}.")


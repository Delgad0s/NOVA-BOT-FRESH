import requests
import os
import re
import unicodedata
from datetime import datetime
from dateutil import parser

FRED_API_KEY = os.getenv("FRED_API_KEY")

# Mapas de series por nombre institucional
SERIES_ID = {
    "inflacion": "CPIAUCSL",
    "pib": "GDP",
    "desempleo": "UNRATE",
    "tasa": "FEDFUNDS",
    "m2": "M2",
    "pce": "PCE"
}

MESES = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "setiembre": "09", "octubre": "10",
    "noviembre": "11", "diciembre": "12"
}

def normalize(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').lower()

def detectar_serie(texto):
    texto = normalize(texto)
    if "pib" in texto: return "pib"
    if "desempleo" in texto or "unrate" in texto: return "desempleo"
    if "cpi" in texto or "inflacion" in texto or "inflación" in texto: return "inflacion"
    if "tasa" in texto or "interes" in texto or "interés" in texto or "fedfunds" in texto: return "tasa"
    if "m2" in texto: return "m2"
    if "pce" in texto: return "pce"
    return None

def extraer_fecha(texto):
    texto = normalize(texto)
    hoy = datetime.today()
    if "hoy" in texto:
        return hoy.strftime("%Y-%m-%d")
    if "ayer" in texto:
        return (hoy - timedelta(days=1)).strftime("%Y-%m-%d")
    for mes, num in MESES.items():
        match = re.search(rf"{mes}\s+(\d{{4}})", texto)
        if match:
            return f"{match.group(1)}-{num}-01"
    # Último intento con parser (no recomendable si ya tienes formato)
    try:
        for palabra in texto.split():
            fecha = parser.parse(palabra, fuzzy=True, dayfirst=False)
            return fecha.strftime("%Y-%m-%d")
    except:
        return None

def obtener_dato_macro(texto):
    tipo = detectar_serie(texto)
    fecha = extraer_fecha(texto)
    if not tipo:
        return "❌ No entendí qué dato macroeconómico quieres (¿inflación, PIB, desempleo, tasa...?)."

    serie_id = SERIES_ID[tipo]
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": serie_id,
        "api_key": FRED_API_KEY,
        "file_type": "json"
    }
    if fecha:
        params["observation_start"] = fecha
        params["observation_end"] = fecha

    r = requests.get(url, params=params)
    if r.status_code != 200:
        return "❌ Error al consultar FRED."

    obs = r.json().get("observations", [])
    if not obs:
        return f"⚠️ No hay datos disponibles para esa fecha."

    dato = obs[0]["value"]
    fecha_dato = obs[0]["date"]

    try:
        valor = float(dato)
        if tipo == "inflacion":
            return f"📊 La inflación intermensual (CPI) de EE.UU. en {fecha_dato} fue de **{valor:.1f}%**."
        elif tipo == "pib":
            return f"📈 El PIB real de EE.UU. en {fecha_dato} fue de **{valor:.2f} billones de USD**."
        elif tipo == "desempleo":
            return f"📉 La tasa de desempleo en {fecha_dato} fue de **{valor:.1f}%**."
        elif tipo == "tasa":
            return f"💰 La tasa de interés en EE.UU. (FEDFUNDS) en {fecha_dato} fue de **{valor:.2f}%**."
        elif tipo == "pce":
            return f"📦 El índice de gastos del consumidor (PCE) en {fecha_dato} fue de **{valor:.2f} puntos**."
        elif tipo == "m2":
            return f"💵 La oferta monetaria M2 en EE.UU. en {fecha_dato} fue de **{valor:.2f} billones USD**."
        else:
            return f"🔍 {tipo.title()} en {fecha_dato}: {valor}"
    except:
        return f"⚠️ Dato recibido: `{dato}` (no se pudo convertir a número)."

def obtener_ultimos_datos_macro():
    resultados = []
    series = {
        "PIB real trimestral (GDPC1)": "GDPC1",
        "Tasa de desempleo (UNRATE)": "UNRATE",
        "Inflación (CPIAUCSL)": "CPIAUCSL",
        "Tasa de interés (FEDFUNDS)": "FEDFUNDS",
        "Tasa hipotecaria 30 años (MORTGAGE30US)": "MORTGAGE30US"
    }
    for nombre, serie_id in series.items():
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": serie_id,
            "api_key": FRED_API_KEY,
            "file_type": "json"
        }
        r = requests.get(url, params=params)
        data = r.json()
        obs = data.get("observations", [])
        if obs:
            valor = obs[-1]["value"]
            try:
                redondeado = round(float(valor), 2)
                resultados.append(f"✅ {nombre}: {redondeado}")
            except:
                resultados.append(f"⚠️ {nombre}: {valor} (no numérico)")
        else:
            resultados.append(f"❌ {nombre}: no disponible")
    return "📊 **Últimos datos macroeconómicos relevantes:**\n" + "\n".join(resultados)

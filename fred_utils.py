import requests
import os
from datetime import datetime
from dateutil import parser

FRED_API_KEY = os.getenv("FRED_API_KEY")

# Diccionario de series clave
SERIES_ID = {
    "inflacion": "CPIAUCNS",
    "pib": "GDP",
    "desempleo": "UNRATE",
    "tasa": "FEDFUNDS",
    "m2": "M2",
    "pce": "PCE"
}

def formatear_fecha(fecha_obj):
    return fecha_obj.strftime("%Y-%m-%d")

def obtener_fecha_actual():
    return datetime.today().strftime("%Y-%m-%d")

def detectar_serie(texto):
    texto = texto.lower()
    if "pib" in texto: return "pib"
    if "desempleo" in texto or "unrate" in texto: return "desempleo"
    if "cpi" in texto or "inflacion" in texto or "inflación" in texto: return "inflacion"
    if "tasa" in texto or "interés" in texto or "interes" in texto: return "tasa"
    if "m2" in texto: return "m2"
    if "pce" in texto: return "pce"
    return None

def obtener_fecha(texto):
    try:
        for palabra in texto.split():
            try:
                fecha = parser.parse(palabra, fuzzy=True, dayfirst=False)
                return formatear_fecha(fecha)
            except:
                continue
        return None
    except:
        return None

def obtener_dato_macro(texto):
    tipo = detectar_serie(texto)
    fecha = obtener_fecha(texto)
    if not tipo:
        return "No entendí qué dato macroeconómico quieres (¿inflación, PIB, desempleo, tasa...?)."

    serie_id = SERIES_ID.get(tipo)
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": serie_id,
        "api_key": FRED_API_KEY,
        "file_type": "json"
    }

    if fecha:
        params["observation_start"] = fecha
        params["observation_end"] = fecha

    respuesta = requests.get(url, params=params)
    if respuesta.status_code != 200:
        return "Error al consultar FRED."

    datos = respuesta.json()
    observaciones = datos.get("observations", [])

    if not observaciones:
        return f"No hay datos disponibles para esa fecha. Intenta con otra."

    dato = observaciones[0]["value"]
    fecha_dato = observaciones[0]["date"]

    try:
        valor_float = float(dato)
        if tipo == "inflacion":
            return f"📊 La inflación (CPI) de EE.UU. en {fecha_dato} fue de aproximadamente {valor_float:.1f} puntos del índice base (no %)."
        elif tipo == "pib":
            return f"📈 El PIB de EE.UU. en {fecha_dato} fue de {valor_float:.2f} billones de dólares (USD)."
        elif tipo == "desempleo":
            return f"📉 La tasa de desempleo en {fecha_dato} fue de {valor_float:.1f}%."
        elif tipo == "tasa":
            return f"💰 La tasa de interés en EE.UU. en {fecha_dato} fue de {valor_float:.2f}%."
        elif tipo == "pce":
            return f"📦 El índice PCE de {fecha_dato} fue de {valor_float:.2f} puntos."
        elif tipo == "m2":
            return f"💵 La oferta monetaria M2 de EE.UU. en {fecha_dato} fue de {valor_float:.2f} billones de dólares."
        else:
            return f"ℹ️ El valor de {tipo} fue {valor_float} en {fecha_dato}."
    except:
        return f"❓ Dato recibido: {dato} (sin formato numérico claro)."

def obtener_ultimos_datos_macro():
    resultados = []
    series = {
        "PIB real trimestral (GDPC1)": "GDPC1",
        "Tasa de desempleo (UNRATE)": "UNRATE",
        "Inflación (CPI) (CPIAUCSL)": "CPIAUCSL",
        "Tasa de interés (FEDFUNDS)": "FEDFUNDS",
        "Tasa hipotecaria 30 años (MORTGAGE30US)": "MORTGAGE30US"
    }
    for nombre, serie_id in series.items():
        url = f"https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": serie_id,
            "api_key": FRED_API_KEY,
            "file_type": "json"
        }
        r = requests.get(url, params=params)
        data = r.json()
        obs = data.get("observations", [])
        if obs:
            valor = float(obs[-1]["value"])
            redondeado = round(valor, 2) if redondeado != "." else valor
            resultados.append(f"✅ {nombre}: {redondeado}")
        else:
            resultados.append(f"❌ {nombre}: no disponible")
    return "📊 Últimos datos macroeconómicos relevantes:\n" + "\n".join(resultados)

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

# Sinónimos para cada serie
SINONIMOS_SERIES = {
    "inflacion": ["inflacion", "inflación", "cpi", "precio consumidor", "índice de precios"],
    "pib": ["pib", "producto interno bruto", "gdp"],
    "desempleo": ["desempleo", "tasa de desempleo", "unrate", "paro"],
    "tasa": ["tasa", "interés", "interes", "federal funds", "fed funds"],
    "m2": ["m2", "oferta monetaria"],
    "pce": ["pce", "consumo personal"]
}

def formatear_fecha(fecha_obj):
    return fecha_obj.strftime("%Y-%m-%d")

def detectar_serie(texto):
    texto = texto.lower()
    for clave, sinonimos in SINONIMOS_SERIES.items():
        if any(palabra in texto for palabra in sinonimos):
            return clave
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
            return f"La inflación (CPI) de EE.UU. en {fecha_dato} fue de aproximadamente {valor_float:.1f} puntos del índice base (no %)."
        elif tipo == "pib":
            return f"El PIB de EE.UU. en {fecha_dato} fue de {valor_float:.2f} billones de dólares (USD)."
        elif tipo == "desempleo":
            return f"La tasa de desempleo en {fecha_dato} fue de {valor_float:.1f}%."
        elif tipo == "tasa":
            return f"La tasa de interés en EE.UU. en {fecha_dato} fue de {valor_float:.2f}%."
        elif tipo == "pce":
            return f"El índice PCE de {fecha_dato} fue de {valor_float:.2f} puntos."
        elif tipo == "m2":
            return f"La oferta monetaria M2 de EE.UU. en {fecha_dato} fue de {valor_float:.2f} billones de dólares."
        else:
            return f"El valor de {tipo} fue {valor_float} en {fecha_dato}."
    except:
        return f"Dato recibido: {dato} (sin formato numérico claro)."

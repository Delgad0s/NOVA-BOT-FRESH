import os
import requests
import unicodedata
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from gpt_utils import ask_nova

# Normaliza texto: sin tildes ni mayúsculas
def normalize(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

# Diccionario meses
MESES = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "setiembre": "09", "octubre": "10",
    "noviembre": "11", "diciembre": "12"
}

def extraer_fecha(texto):
    for mes_es, mes_num in MESES.items():
        match = re.search(rf"{mes_es}\s+(\d{{4}})", texto)
        if match:
            anio = match.group(1)
            return f"{anio}-{mes_num}-01"
    return None

def obtener_cpi_por_fecha(fecha):
    api_key = os.getenv("FRED_API_KEY")
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key={api_key}&file_type=json"
    r = requests.get(url)
    data = r.json()
    for obs in data["observations"]:
        if obs["date"] == fecha:
            return obs["value"]
    return None

async def manejar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    normalizado = normalize(texto)
    fecha_fred = extraer_fecha(normalizado)

    if any(p in normalizado for p in ["cpi", "inflacion"]) and fecha_fred:
        valor = obtener_cpi_por_fecha(fecha_fred)
        if valor:
            mes = list(MESES.keys())[list(MESES.values()).index(fecha_fred[5:7])]
            anio = fecha_fred[:4]
            mensajes = [
                {"role": "system", "content": "Eres un analista macroeconómico profesional. Usa el dato que se te proporciona para responder como si fueras ChatGPT con acceso a datos reales."},
                {"role": "user", "content": f"El CPI de EE.UU. en {mes} de {anio} fue {valor}%. ¿Qué implica esto para la inflación y la economía actual?"}
            ]
            respuesta = ask_nova(mensajes)
            await update.message.reply_text(respuesta)
            return
        else:
            await update.message.reply_text("⚠️ No encontré datos exactos para esa fecha en FRED.")
            return

    # GPT libre si no se detectó intención clara
    respuesta = ask_nova([{"role": "user", "content": texto}])
    await update.message.reply_text(respuesta)

# Lanzar bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar))
    app.run_polling()

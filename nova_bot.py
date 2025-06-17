import os
import requests
import unicodedata
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from gpt_utils import ask_nova

# 🔧 Normalizar texto (sin tildes ni mayúsculas)
def normalize(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

# 📆 Diccionario para extraer fechas de usuario
MESES = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "setiembre": "09", "octubre": "10",
    "noviembre": "11", "diciembre": "12"
}

def extraer_fecha(texto):
    for mes, numero in MESES.items():
        match = re.search(rf"{mes}\s+(\d{{4}})", texto)
        if match:
            anio = match.group(1)
            return f"{anio}-{numero}-01"
    return None

def obtener_cpi_por_fecha(fecha_fred):
    api_key = os.getenv("FRED_API_KEY")
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key={api_key}&file_type=json"
    r = requests.get(url)
    data = r.json()
    for obs in data["observations"]:
        if obs["date"] == fecha_fred:
            return obs["value"]
    return None

async def manejar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_original = update.message.text
    texto = normalize(texto_original)

    # 🧠 Detecta intención de dato FRED
    fecha_fred = extraer_fecha(texto)
    if any(p in texto for p in ["cpi", "inflacion"]) and fecha_fred:
        valor = obtener_cpi_por_fecha(fecha_fred)
        if valor:
            mes_es = list(MESES.keys())[list(MESES.values()).index(fecha_fred[5:7])]
            anio = fecha_fred[:4]
            # 🎯 GPT responde usando el dato de FRED
            respuesta = ask_nova([
                {"role": "system", "content": "Eres un analista macroeconómico profesional que responde con precisión y claridad usando datos reales."},
                {"role": "user", "content": f"El CPI de EE.UU. en {mes_es} de {anio} fue {valor}%. ¿Qué significa eso para la inflación y la economía actual?"}
            ])
            await update.message.reply_text(respuesta)
            return

    # 🧠 Si no hay intención clara → usa GPT-4o libre
    reply = ask_nova([{"role": "user", "content": texto_original}])
    await update.message.reply_text(reply)

# 🚀 Lanzamiento del bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar))
    app.run_polling()

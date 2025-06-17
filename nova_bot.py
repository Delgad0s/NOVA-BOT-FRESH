import os
import requests
import unicodedata
import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, MessageHandler, ContextTypes, filters
)
from gpt_utils import ask_nova

# 🔧 Normalizador para quitar tildes
def normalize(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

# 📆 Diccionario español-inglés de meses
MESES = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "setiembre": "09", "octubre": "10",
    "noviembre": "11", "diciembre": "12"
}

# 🧠 Extrae fecha en formato YYYY-MM-01
def extraer_fecha(texto):
    for mes_es, mes_num in MESES.items():
        match = re.search(rf"{mes_es}\s+(\d{{4}})", texto)
        if match:
            anio = match.group(1)
            return f"{anio}-{mes_num}-01"
    return None

# 📊 Consulta FRED y devuelve dato de fecha exacta
def obtener_cpi_por_fecha(fecha_buscada):
    api_key = os.getenv("FRED_API_KEY")
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key={api_key}&file_type=json"
    r = requests.get(url)
    data = r.json()
    for obs in data["observations"]:
        if obs["date"] == fecha_buscada:
            return obs["value"]
    return None

# 🤖 GPT-4o como fallback
async def responder_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = [{"role": "user", "content": update.message.text}]
    reply = ask_nova(messages)
    await update.message.reply_text(reply)

# 🎯 Manejador principal
async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_original = update.message.text
    texto = normalize(texto_original)

    fecha_fred = extraer_fecha(texto)
    if fecha_fred:
        print("🟡 Se detectó una fecha:", fecha_fred)
        valor = obtener_cpi_por_fecha(fecha_fred)
        if valor:
            anio, mes, _ = fecha_fred.split("-")
            mes_es = list(MESES.keys())[list(MESES.values()).index(mes)]
            await update.message.reply_text(
                f"📈 El CPI de EE.UU. en {mes_es.capitalize()} de {anio} fue {valor}%"
            )
        else:
            await update.message.reply_text("⚠️ No encontré datos para esa fecha en FRED.")
    elif any(palabra in texto for palabra in ["cpi", "inflacion", "indice de precios", "datos de inflacion"]):
        await update.message.reply_text("📌 Especifica un mes y año, por ejemplo: 'CPI mayo 2025'")
    else:
        await responder_gpt(update, context)

# 🚀 Iniciar bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))
    app.run_polling()

import os
import re
import unicodedata
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from gpt_utils import ask_nova
from fred_utils import obtener_dato_macro

MESES = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "setiembre": "09", "octubre": "10",
    "noviembre": "11", "diciembre": "12"
}

def normalize(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def extraer_fecha(texto):
    texto = normalize(texto)
    hoy = datetime.now()
    if "hoy" in texto:
        return hoy.strftime("%Y-%m-%d")
    elif "ayer" in texto:
        return (hoy - timedelta(days=1)).strftime("%Y-%m-%d")
    for mes_es, mes_num in MESES.items():
        match = re.search(rf"{mes_es}\s+(\d{{4}})", texto)
        if match:
            anio = match.group(1)
            return f"{anio}-{mes_num}-01"
    return None

def tiene_palabra_clave(texto):
    claves = ["inflacion", "cpi", "pib", "desempleo", "tasa", "interes", "fedfunds", "m2", "pce"]
    return any(p in normalize(texto) for p in claves)

async def manejar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    normalizado = normalize(texto)

    # Pregunta de fecha
    if "que dia es hoy" in normalizado or "fecha de hoy" in normalizado:
        hoy = datetime.now().strftime("%A, %d de %B de %Y")
        await update.message.reply_text(f"Hoy es {hoy}.")
        return

    # Intención macroeconómica (usa FRED)
    if tiene_palabra_clave(normalizado):
        respuesta = obtener_dato_macro(texto)
        await update.message.reply_text(respuesta)
        return

    # GPT libre
    respuesta = ask_nova([{"role": "user", "content": texto}])
    await update.message.reply_text(respuesta)

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar))
    app.run_polling()

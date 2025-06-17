import os
import requests
import unicodedata
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from gpt_utils import ask_nova
from fred_utils import obtener_dato_macro

# Normaliza texto: sin tildes ni mayúsculas
def normalize(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

# Diccionario de meses en español
MESES = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "setiembre": "09", "octubre": "10",
    "noviembre": "11", "diciembre": "12"
}

# Extrae fechas tipo "mayo 2025"
def extraer_fecha(texto):
    texto = normalize(texto)
    for mes_es, mes_num in MESES.items():
        match = re.search(rf"{mes_es}\s+(\d{{4}})", texto)
        if match:
            anio = match.group(1)
            return f"{anio}-{mes_num}-01"
    return None

# Manejador de mensajes
async def manejar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    texto_normalizado = normalize(texto)
    fecha_fred = extraer_fecha(texto_normalizado)

    # Si detectamos intención macroeconómica
    if any(p in texto_normalizado for p in ["cpi", "inflacion", "pib", "tasa", "desempleo", "unrate", "m2", "pce"]):
        mensaje = texto
        if fecha_fred:
            mensaje += f" {fecha_fred}"
        respuesta = obtener_dato_macro(mensaje)
        await update.message.reply_text(respuesta)
        return

    # GPT-4o libre si no detectamos nada
    respuesta = ask_nova([{"role": "user", "content": texto}])
    await update.message.reply_text(respuesta)

# Lanzar bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar))
    app.run_polling()

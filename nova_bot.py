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

# Diccionario meses
MESES = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "setiembre": "09", "octubre": "10",
    "noviembre": "11", "diciembre": "12"
}

def extraer_fecha(texto):
    for mes_es, mes_num in MESES.items():
        match = re.search(rf"{mes_es}\\s+(\\d{{4}})", texto)
        if match:
            anio = match.group(1)
            return f"{anio}-{mes_num}-01"
    return None

async def manejar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    normalizado = normalize(texto)

    # 1. Intenta detectar y responder con un dato macroeconómico
    respuesta_dato = obtener_dato_macro(texto)
    if not respuesta_dato.startswith("No entendí") and not respuesta_dato.startswith("Error") and "Dato recibido" not in respuesta_dato:
        # 2. Si se obtuvo un dato válido, genera una respuesta GPT a partir del dato
        mensajes = [
            {"role": "system", "content": "Eres un analista macroeconómico profesional. Usa el dato que se te proporciona para responder como si fueras ChatGPT con acceso a datos reales."},
            {"role": "user", "content": respuesta_dato + " ¿Qué implica esto para la economía actual de EE.UU.?"}
        ]
        respuesta = ask_nova(mensajes)
        await update.message.reply_text(respuesta)
        return

    # 3. GPT libre si no se detectó un dato macroeconómico
    respuesta = ask_nova([{"role": "user", "content": texto}])
    await update.message.reply_text(respuesta)

# Lanzar bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar))
    app.run_polling()

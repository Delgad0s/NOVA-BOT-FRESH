import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, MessageHandler, ContextTypes, filters
)
from gpt_utils import ask_nova  # GPT-4o

# 🔍 FRED: CPI de EE.UU.
async def responder_fred(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api_key = os.getenv("FRED_API_KEY")
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key={api_key}&file_type=json"

    response = requests.get(url)
    data = response.json()

    if "observations" in data:
        valores = data["observations"][-3:]
        mensaje = "📊 Últimos 3 datos de inflación (CPI - EE.UU.):\n\n"
        for obs in valores:
            mensaje += f"{obs['date']}: {obs['value']}\n"
        await update.message.reply_text(mensaje)
    else:
        await update.message.reply_text("⚠️ No se pudieron obtener datos de FRED.")

# 🤖 GPT-4o para análisis institucional
async def responder_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    messages = [{"role": "user", "content": user_input}]
    try:
        reply = ask_nova(messages)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("⚠️ Error al procesar con GPT-4o.")

# 🧠 Manejador inteligente de mensajes
async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    if any(palabra in texto for palabra in ["inflación", "cpi", "índice de precios", "eeuu", "ee.uu", "datos de inflación"]):
        await responder_fred(update, context)
    else:
        await responder_gpt(update, context)

# 🚀 Inicialización del bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))
    app.run_polling()

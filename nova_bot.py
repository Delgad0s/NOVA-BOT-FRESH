from telegram.ext import ApplicationBuilder, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
import os
import requests

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "inflación" in update.message.text.lower():
        api_key = os.getenv("FRED_API_KEY")
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key={api_key}&file_type=json"
        
        response = requests.get(url)
        data = response.json()
        
        print("🟢 DEBUG: Respuesta FRED:", data)  # 👈 Saldrá en los LOGS de Railway

        if "observations" in data:
            valores = data["observations"][-12:]
            mensaje = "📊 Últimos 12 datos de inflación (CPI - EE.UU.):\n\n"
            for obs in valores:
                mensaje += f"{obs['date']}: {obs['value']}\n"
            await update.message.reply_text(mensaje)
        else:
            await update.message.reply_text("Error: No se pudieron obtener datos de FRED.")
    else:
        await update.message.reply_text("¿Qué dato deseas consultar? Puedes pedirme inflación de EE.UU.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.run_polling()

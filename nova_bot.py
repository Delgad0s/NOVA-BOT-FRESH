import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from gpt_utils import ask_nova
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ No se encontró TELEGRAM_BOT_TOKEN en las variables de entorno.")

application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

# 👇 Manejador de mensajes
@application.message()
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        texto = update.message.text
        print(f"[🟡 MENSAJE RECIBIDO] {texto}")
        
        respuesta = ask_nova([{"role": "user", "content": texto}])
        
        print(f"[🟢 RESPUESTA ENVIADA] {respuesta}")
        await update.message.reply_text(respuesta)
    except Exception as e:
        print(f"[❌ ERROR EN EL MANEJO DE MENSAJE] {e}")
        await update.message.reply_text(f"❌ Error interno: {e}")

# 👇 Iniciar bot
if __name__ == "__main__":
    print("🚀 NOVA iniciando...")
    application.run_polling()

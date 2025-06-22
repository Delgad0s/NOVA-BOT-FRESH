import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters
)

from gpt_utils import ask_nova  # <-- Importa tu función GPT-4o

# Cargar variables de entorno
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configurar logging (opcional pero útil)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Handler para mensajes de texto
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    messages = [{"role": "user", "content": user_input}]
    
    try:
        reply = ask_nova(messages)
        await update.message.reply_text(reply)
    except Exception as e:
        logging.error(f"Error al generar respuesta con GPT-4o: {e}")
        await update.message.reply_text("Hubo un error procesando tu solicitud.")

# Construir la aplicación del bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # app.run_polling()

if __name__ == "__main__":
    main()


import os
from openai import OpenAI
from dotenv import load_dotenv
from fred_utils import obtener_dato_macro  # <- Importación clave

# Cargar variables de entorno
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def ask_nova(messages):
    texto_usuario = messages[-1]["content"].lower()

    # Paso 1: Detectar si es macro
    if any(palabra in texto_usuario for palabra in ["inflacion", "inflación", "pib", "desempleo", "tasa", "pce", "m2"]):
        resultado_macro = obtener_dato_macro(texto_usuario)
        if resultado_macro:
            return resultado_macro

    # Paso 2: GPT como fallback
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al generar respuesta con GPT-4o: {e}"

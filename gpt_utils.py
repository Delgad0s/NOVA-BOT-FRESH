import openai
import os

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INSTITUTIONAL_PROMPT = {
    "role": "system",
    "content": (
        "Actúa como NOVA, un asistente institucional experto en macroeconomía, geopolítica y mercados globales. "
        "Responde con análisis táctico, en tono frío, directo y profesional. Usa un enfoque estructurado y preciso. "
        "Evita opiniones genéricas o suposiciones no verificadas. Hablas en español. Tu usuario es un analista profesional."
    )
}

def ask_nova(messages):
    full_prompt = [INSTITUTIONAL_PROMPT] + messages
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=full_prompt,
        temperature=0.3
    )
    return response.choices[0].message.content

import os
from openai import OpenAI

# Crear cliente
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_nova(messages):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3
    )
    return response.choices[0].message.content

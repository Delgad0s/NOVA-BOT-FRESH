import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_nova(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3
    )
    return response['choices'][0]['message']['content']

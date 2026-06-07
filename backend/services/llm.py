import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def get_client():
    return Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )


def generate_response(prompt: str):
    client = get_client()

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful product research assistant that analyzes user interviews and extracts insights with evidence."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


def stream_response(prompt: str):
    client = get_client()

    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
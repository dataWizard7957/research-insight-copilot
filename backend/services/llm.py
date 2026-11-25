import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# llama-3.1-8b-instant was retired by Groq on 2026-08-16; gpt-oss-20b is
# Groq's recommended replacement. Override with GROQ_MODEL if it changes again.
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def _extra_args() -> dict:
    # gpt-oss models reason before answering; keep that short for snappy replies.
    return {"reasoning_effort": "low"} if MODEL.startswith("openai/gpt-oss") else {}


def get_client():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is not set on the server")
    return Groq(api_key=key)


def generate_response(prompt: str):
    client = get_client()

    response = client.chat.completions.create(
        model=MODEL,
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
        **_extra_args(),
    )

    return response.choices[0].message.content


def stream_response(prompt: str):
    client = get_client()

    stream = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        stream=True,
        **_extra_args(),
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta

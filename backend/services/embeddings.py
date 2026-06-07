import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

# Local embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str):
    return model.encode(text).tolist()
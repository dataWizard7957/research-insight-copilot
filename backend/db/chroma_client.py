import os

import chromadb

client = chromadb.PersistentClient(path=os.getenv("CHROMA_PATH", "./chroma_db"))

collection = client.get_or_create_collection(
    name="interviews"
)

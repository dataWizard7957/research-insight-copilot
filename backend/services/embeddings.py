"""
Sentence embeddings with all-MiniLM-L6-v2, run through ONNX Runtime
(ChromaDB's built-in embedder). Same model as sentence-transformers, without
PyTorch, so the backend installs in ~100 MB and starts quickly.
"""
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

_embed = DefaultEmbeddingFunction()


def get_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    return [[float(x) for x in v] for v in _embed(texts)]


def get_embedding(text: str) -> list[float]:
    return get_embeddings([text])[0]

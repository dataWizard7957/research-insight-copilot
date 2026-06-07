from fastapi import APIRouter
from db.chroma_client import collection
from collections import defaultdict

router = APIRouter()

@router.get("/")
def get_transcripts():
    results = collection.get()

    docs = results.get("documents", [])
    metas = results.get("metadatas", [])

    grouped = defaultdict(lambda: {
        "id": None,
        "chunk_id": None,
        "transcript_id": None,
        "filename": None,
        "sentences": []
    })

    for d, m in zip(docs, metas):
        key = (m["transcript_id"], m["chunk_id"])

        if grouped[key]["id"] is None:
            grouped[key]["id"] = f"{m['transcript_id']}_{m['chunk_id']}"
            grouped[key]["chunk_id"] = m["chunk_id"]
            grouped[key]["transcript_id"] = m["transcript_id"]
            grouped[key]["filename"] = m.get("filename")  

        grouped[key]["sentences"].append({
            "sentence_id": m["sentence_id"],
            "text": d
        })

    return list(grouped.values())
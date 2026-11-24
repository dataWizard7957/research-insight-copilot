import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from deps import workspace
from db.chroma_client import collection
from services.rag import add_chunks, clean_transcript
from utils.chunking import chunk_text

router = APIRouter()

MAX_BYTES = 300 * 1024  # interview transcripts are plain text; 300 KB is plenty
ALLOWED = {".txt", ".md"}
SAMPLES = Path(__file__).resolve().parent.parent / "samples"


def _store(text: str, filename: str, ws: str) -> dict:
    text = clean_transcript(text)
    chunks = chunk_text(text)
    doc_id = str(uuid.uuid4())
    sentences = add_chunks(chunks=chunks, doc_id=doc_id, filename=filename, ws=ws)
    return {"transcript_id": doc_id, "filename": filename, "chunks_created": len(chunks), "sentences": sentences}


@router.post("/")
async def upload_file(file: UploadFile = File(...), ws: str = Depends(workspace)):
    name = file.filename or "transcript.txt"
    if Path(name).suffix.lower() not in ALLOWED:
        raise HTTPException(415, "Upload a .txt or .md transcript")
    content = await file.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise HTTPException(413, "Transcript is larger than 300 KB")

    result = _store(content.decode("utf-8", errors="ignore"), name, ws)
    return {"message": "Transcript uploaded successfully", **result}


@router.post("/sample")
def load_samples(ws: str = Depends(workspace)):
    """Load the bundled sample interviews into this workspace (once)."""
    loaded = []
    for path in sorted(SAMPLES.glob("*.txt")):
        exists = collection.get(where={"$and": [{"workspace": ws}, {"filename": path.name}]}, limit=1)
        if exists["ids"]:
            continue
        loaded.append(_store(path.read_text(encoding="utf-8"), path.name, ws))
    return {"message": f"Loaded {len(loaded)} sample interviews", "loaded": loaded}

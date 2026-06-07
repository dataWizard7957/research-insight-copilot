from fastapi import APIRouter, UploadFile, File
import uuid

from utils.chunking import chunk_text
from services.rag import add_chunks, clean_transcript  # ✅ IMPORTANT FIX

router = APIRouter()


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()

    # ==================================================
    # STEP 1: decode safely
    # ==================================================
    text = content.decode("utf-8", errors="ignore")

    # ==================================================
    # STEP 2: CLEAN TRANSCRIPT (CRITICAL FIX)
    # ==================================================
    text = clean_transcript(text)

    # ==================================================
    # STEP 3: generate chunks
    # ==================================================
    chunks = chunk_text(text)

    # ==================================================
    # STEP 4: unique doc id
    # ==================================================
    doc_id = str(uuid.uuid4())

    # ==================================================
    # STEP 5: store in vector DB
    # ==================================================
    add_chunks(
        chunks=chunks,
        doc_id=doc_id,
        filename=file.filename
    )
    


    return {
        "message": "Transcript uploaded successfully",
        "transcript_id": doc_id,
        "chunks_created": len(chunks)
    }
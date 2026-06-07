from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from services.rag import query_rag
from services.llm import stream_response

router = APIRouter()


# =========================
# REQUEST MODEL
# =========================

class ChatRequest(BaseModel):
    question: str
    sources: Optional[List[Dict[str, Any]]] = []


# =========================
# NORMAL RAG CHAT
# =========================

@router.post("/")
def chat(req: ChatRequest):
    return query_rag(req.question)


# =========================
# STREAMING CHAT
# =========================

@router.post("/stream")
def chat_stream(req: ChatRequest):

    try:

        rag_result = query_rag(req.question)

        context = {
            "rag_result": rag_result,
            "selected_sources": req.sources,
        }

        prompt = f"""
You are a senior customer research assistant.

Use ONLY the provided context.

Context:
{context}

Question:
{req.question}

Rules:
- Be concise
- Use evidence from context
- If context is insufficient, say so
"""

        return StreamingResponse(
            stream_response(prompt),
            media_type="text/plain",
        )

    except Exception as e:
        return StreamingResponse(
            iter([f"Error: {str(e)}"]),
            media_type="text/plain",
        )
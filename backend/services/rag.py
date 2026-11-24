import json
import re

import numpy as np

from db.chroma_client import collection
from services.embeddings import get_embedding, get_embeddings
from services.llm import generate_response


# ==================================================
# JSON PARSER
# ==================================================

def parse_json_response(text: str):
    """
    Safely parse JSON returned by the LLM.
    """

    if not text:
        raise ValueError("Empty LLM response")

    text = text.strip()

    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    return json.loads(text)


# ==================================================
# CLEANING
# ==================================================


def clean_transcript(text: str) -> str:
    """
    Remove UI noise + frontend artifacts BEFORE chunking.
    """

    # UI garbage removal (YOUR EXACT BUG)
    text = re.sub(r"📤 Upload.*", "", text)
    text = re.sub(r"💬 Chat.*", "", text)
    text = re.sub(r"📊 Insights.*", "", text)
    text = re.sub(r"📄 Transcripts.*", "", text)
    text = re.sub(r"Ask follow-up.*", "", text)

    # interview labels
    # Interviewer questions are not evidence: drop those lines entirely
    # (needs the original line breaks, so this runs before whitespace is collapsed).
    text = re.sub(r"(?im)^\s*(Interviewer|Q):.*$", "", text)
    text = re.sub(r"Participant:\s*", "", text)
    text = re.sub(r"Interview Date:.*", "", text)

    # normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def split_sentences(text: str):
    """
    Clean + split into meaningful sentences.
    """

    text = clean_transcript(text)

    sentences = re.split(r"(?<=[.!?])\s+", text)

    return [
        s.strip()
        for s in sentences
        if len(s.strip()) > 12
    ]


# ==================================================
# STORE TRANSCRIPTS
# ==================================================

def add_chunks(chunks, doc_id: str, filename: str, ws: str = "default"):
    """
    Store transcript sentences in ChromaDB, tagged with the visitor's workspace.
    All sentences are embedded in one batch.
    """

    ids, docs, metas = [], [], []
    for chunk_id, chunk in enumerate(chunks):
        for sentence_id, sentence in enumerate(split_sentences(chunk)):
            ids.append(f"{ws}_{doc_id}_{chunk_id}_{sentence_id}")
            docs.append(sentence)
            metas.append({
                "workspace": ws,
                "transcript_id": doc_id,
                "filename": filename,
                "chunk_id": chunk_id,
                "sentence_id": sentence_id,
            })

    if not docs:
        return 0

    collection.add(ids=ids, documents=docs, embeddings=get_embeddings(docs), metadatas=metas)
    return len(docs)


def get_workspace(ws: str, embeddings: bool = False):
    include = ["documents", "metadatas"] + (["embeddings"] if embeddings else [])
    return collection.get(where={"workspace": ws}, include=include)


# ==================================================
# RAG CHAT
# ==================================================

def query_rag(question: str, ws: str = "default", top_k: int = 5):

    query_embedding = get_embedding(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"workspace": ws},
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    if not docs:
        return {
            "answer": "No research transcripts uploaded yet.",
            "themes": [],
            "key_quotes": [],
            "sources": []
        }

    context = "\n\n".join(docs[:4])

    prompt = f"""
You are an expert customer research analyst.

Use ONLY provided interview evidence.

Return ONLY valid JSON.

Format:
{{
  "answer": "",
  "themes": [
    {{
      "name": ""
    }}
  ],
  "key_quotes": []
}}

Context:
{context}

Question:
{question}
"""

    response = generate_response(prompt)

    try:
        parsed = parse_json_response(response)

        sources = []
        for doc, meta in zip(docs[:3], metas[:3]):
            sources.append({
                "text": doc,
                "filename": meta.get("filename"),
                "transcript_id": meta.get("transcript_id"),
                "chunk_id": meta.get("chunk_id"),
                "sentence_id": meta.get("sentence_id"),
            })

        parsed["sources"] = sources
        return parsed

    except Exception as e:
        return {
            "error": str(e),
            "raw_response": response,
        }


# ==================================================
# INSIGHTS GENERATION (FIXED EVIDENCE SYSTEM)
# ==================================================

def generate_insights(ws: str = "default"):

    results = get_workspace(ws, embeddings=True)
    documents = results.get("documents") or []
    metadatas = results.get("metadatas") or []
    stored = results.get("embeddings")
    doc_matrix = np.asarray(stored, dtype=np.float32) if documents else None

    if not documents:
        return {
            "executive_summary": "No transcripts uploaded yet.",
            "top_themes": [],
            "pain_points": [],
            "feature_requests": [],
            "recommended_actions": [],
        }

    all_text = "\n\n".join(documents)

    # STEP 1: LLM STRUCTURE ONLY
    prompt = f"""
You are a senior customer research analyst.

Analyze interview data.

Return ONLY valid JSON.

Format:
{{
  "executive_summary": "",
  "top_themes": [
    {{
      "name": "",
      "summary": ""
    }}
  ],
  "pain_points": [],
  "feature_requests": [],
  "recommended_actions": []
}}

Data:
{all_text[:12000]}
"""

    response = generate_response(prompt)
    parsed = parse_json_response(response)

    # ==================================================
    # STEP 2: BACKEND ATTACHES REAL EVIDENCE (FIXED)
    # ==================================================

    enriched_themes = []

    for theme in parsed.get("top_themes", []):

        theme_name = theme.get("name", "")
        if not theme_name:
            continue

        # Rank this workspace's sentences against the theme, reusing the
        # embeddings stored at upload time.
        theme_embedding = np.asarray(get_embedding(theme_name), dtype=np.float32)
        scores = doc_matrix @ theme_embedding
        top = [(float(scores[i]), documents[i], metadatas[i]) for i in np.argsort(-scores)[:3]]

        evidence = [
            {
                "text": doc,
                "transcript_id": meta.get("transcript_id"),
                "chunk_id": meta.get("chunk_id"),
                "sentence_id": meta.get("sentence_id"),
                "filename": meta.get("filename"),
            }
            for _, doc, meta in top
        ]

        theme["evidence"] = evidence
        enriched_themes.append(theme)

    parsed["top_themes"] = enriched_themes

    return parsed


# ==================================================
# FOLLOW UPS
# ==================================================

def generate_followups(theme: str):

    prompt = f"""
You are a senior UX researcher.

Theme:
{theme}

Return ONLY valid JSON:
{{
  "questions": ["", "", "", "", ""]
}}

Generate exactly 5 questions.
"""

    response = generate_response(prompt)

    try:
        return parse_json_response(response)
    except Exception as e:
        return {
            "error": str(e),
            "raw_response": response,
        }


# ==================================================
# SUMMARY
# ==================================================

def generate_research_summary(ws: str = "default"):

    results = get_workspace(ws)
    metadatas = results.get("metadatas", [])

    participants = len(set(
        m.get("transcript_id")
        for m in metadatas
        if m
    ))

    insights = generate_insights(ws)

    return {
        "participants": participants,
        "top_themes": insights.get("top_themes", []),
        "common_pain_points": insights.get("pain_points", []),
        "recommended_next_questions": [
            "What part of workflow is slowest?",
            "How are insights shared today?",
            "What improves trust in AI insights?"
        ],
    }


# ==================================================
# FULL REPORT
# ==================================================

def generate_research_report(ws: str = "default"):

    results = get_workspace(ws)
    documents = results.get("documents", [])

    if not documents:
        return {
            "executive_summary": "",
            "top_themes": [],
            "pain_points": [],
            "feature_requests": [],
            "recommended_actions": [],
        }

    all_text = "\n\n".join(documents)

    prompt = f"""
You are a principal customer research strategist.

Return ONLY valid JSON.

Format:
{{
  "executive_summary": "",
  "top_themes": [],
  "pain_points": [],
  "feature_requests": [],
  "recommended_actions": []
}}

Data:
{all_text[:12000]}
"""

    response = generate_response(prompt)

    try:
        return parse_json_response(response)
    except Exception as e:
        return {
            "error": str(e),
            "raw_response": response,
        }
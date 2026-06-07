import json
import re

from db.chroma_client import collection
from services.embeddings import get_embedding
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
    text = re.sub(r"Participant:\s*", "", text)
    text = re.sub(r"Interviewer:\s*", "", text)
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

def add_chunks(chunks, doc_id: str, filename: str):
    """
    Store transcript sentences in ChromaDB.
    """

    for chunk_id, chunk in enumerate(chunks):

        sentences = split_sentences(chunk)

        for sentence_id, sentence in enumerate(sentences):

            embedding = get_embedding(sentence)

            collection.add(
                ids=[f"{doc_id}_{chunk_id}_{sentence_id}"],
                documents=[sentence],
                embeddings=[embedding],
                metadatas=[{
                    "transcript_id": doc_id,
                    "filename": filename,  
                    "chunk_id": chunk_id,
                    "sentence_id": sentence_id,
                }],
            )


# ==================================================
# RAG CHAT
# ==================================================

def query_rag(question: str, top_k: int = 5):

    query_embedding = get_embedding(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
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

def generate_insights():

    results = collection.get()
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

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

        theme_embedding = get_embedding(theme_name)

        # LOCAL semantic ranking (no DB cross-contamination issues)
        scored = []

        for doc, meta in zip(documents, metadatas):
            doc_embedding = get_embedding(doc)

            score = sum(a * b for a, b in zip(theme_embedding, doc_embedding))

            scored.append((score, doc, meta))

        scored.sort(reverse=True, key=lambda x: x[0])

        top = scored[:3]

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

def generate_research_summary():

    results = collection.get()
    metadatas = results.get("metadatas", [])

    participants = len(set(
        m.get("transcript_id")
        for m in metadatas
        if m
    ))

    insights = generate_insights()

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

def generate_research_report():

    results = collection.get()
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
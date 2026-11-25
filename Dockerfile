# Full app in one Hugging Face Space: React frontend + FastAPI backend.
# Build:  docker build -t research-copilot .     Run: docker run -p 7860:7860 -e GROQ_API_KEY=... research-copilot

# ---- 1. Build the React app ----
FROM node:22-alpine AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
# The backend serves the API under /api on the same origin.
ENV VITE_API_URL=/api
RUN npm run build

# ---- 2. Backend, serving the API and the built app ----
FROM python:3.12-slim

# Spaces run containers as user 1000.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    API_PREFIX=/api \
    STATIC_DIR=/home/user/app/static \
    REQUIRE_WORKSPACE=1 \
    CHROMA_PATH=/home/user/app/chroma_db
WORKDIR /home/user/app

COPY --chown=user backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
# Download the ONNX embedding model at build time so the first request is fast.
RUN python -c "from chromadb.utils.embedding_functions import DefaultEmbeddingFunction as E; E()(['warm up'])"

COPY --chown=user backend/ .
COPY --chown=user --from=web /web/dist ./static

EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]

# Research Insight Copilot

Turn customer interview transcripts into themes, pain points and feature requests, each linked to the sentences that support it. Then ask questions about your research in a chat grounded in the transcripts.

## Features

- **Insights:** executive summary, top themes, pain points, feature requests and recommended actions.
- **Evidence:** each theme lists the transcript sentences that best support it. Click one to jump to it in the transcript.
- **Chat:** streamed answers drawn from the most relevant transcript sentences. Select sentences in a transcript to attach them to your question.
- **Follow-up questions:** five suggested interview questions for any theme.
- **Private workspaces:** each browser gets its own isolated workspace, so a public deployment never mixes visitors' data.
- **Sample data:** three fictional interviews to try the app without your own files.

## How it works

1. **Upload.** A transcript (`.txt` or `.md`, up to 300 KB) is cleaned, interviewer lines are removed, and the text is split into sentences.
2. **Index.** Each sentence is embedded with `all-MiniLM-L6-v2` and stored in ChromaDB with its transcript, chunk and sentence position.
3. **Analyze.** Llama 3.1 (via Groq) reads the transcripts and returns structured JSON. The backend then ranks every stored sentence against each theme by embedding similarity and attaches the top matches as evidence.
4. **Chat.** A question retrieves the closest sentences, and the model answers from that context only.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Vector store | ChromaDB |
| Embeddings | `all-MiniLM-L6-v2` on ONNX Runtime (no PyTorch) |
| LLM | Llama 3.1 8B Instant via Groq |
| Frontend | React, Vite, React Router |
| Deployment | Docker, Render |

## Run locally

Requirements: Python 3.12, Node.js 22 and a free [Groq API key](https://console.groq.com).

```bash
# Backend: http://127.0.0.1:8000
cd backend
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key" > .env
uvicorn main:app --reload

# Frontend: http://localhost:5173 (in a second terminal)
cd frontend
npm install
npm run dev
```

Or run the whole app in one container:

```bash
docker build -t research-copilot .
docker run -p 7860:7860 -e GROQ_API_KEY=your_key research-copilot   # http://localhost:7860
```

## Deploy

The root `Dockerfile` builds the frontend and serves it from FastAPI, with the API under `/api`, so the app deploys as a single service.

**Render (free):** choose **New → Blueprint**, select this repository, enter `GROQ_API_KEY` when prompted, and apply. `render.yaml` configures the rest. Pushes to `main` redeploy automatically. Free services sleep after 15 minutes without traffic, so the next visit takes 30–60 seconds, and stored data resets on restart.

Use a Groq account without a payment card for public demos: heavy traffic then hits a rate limit rather than a bill.

## Configuration

| Variable | Where | Purpose |
|---|---|---|
| `GROQ_API_KEY` | Backend | Required for insights and chat |
| `ALLOWED_ORIGINS` | Backend | Comma-separated origins allowed by CORS (default `*`) |
| `VITE_API_URL` | Frontend build | Backend URL (default `http://127.0.0.1:8000`; `/api` in the Docker image) |

## Limitations

- Insights read the first ~12,000 characters of all transcripts combined, so very large collections are only partly analyzed.
- Evidence is matched by semantic similarity. It points to relevant sentences but is not a citation chosen by the model.
- Data lives in a local ChromaDB folder; there are no user accounts.

## Roadmap

- Theme clustering across larger transcript collections
- Report export (PDF, Notion)
- Persistent storage and team workspaces

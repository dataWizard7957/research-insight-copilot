# 🧠 Research Insight Copilot

An AI-powered research tool that transforms interview transcripts into structured insights, themes, and evidence-backed analysis.  
It allows users to upload transcripts, explore sentence-level evidence, and chat with AI grounded in real interview data.

---

## 🚀 Features

- 📤 Upload interview transcripts (TXT files)
- 🧾 Automatic chunking & sentence segmentation
- 🔍 Vector search using embeddings (RAG system)
- 🧠 AI-generated insights (themes, pain points, feature requests)
- 📌 Evidence-backed analysis (clickable transcript sentences)
- 💬 Chat with AI grounded in transcripts
- 🔗 Jump from insights → exact transcript sentence
- 📊 Research summary + follow-up questions

---

## 🏗️ Tech Stack

### Backend
- FastAPI
- ChromaDB (Vector Database)
- SentenceTransformers (`all-MiniLM-L6-v2`)
- Groq LLM (LLaMA 3.1)
- Python

### Frontend
- React (Vite)
- React Router
- Vanilla CSS (inline styles)

---

## 📁 Project Structure

```

Research_Insight_Copilot/
│
├── backend/
│   ├── main.py
│   ├── db/
│   │   └── chroma_client.py
│   │
│   ├── routes/
│   │   ├── upload.py
│   │   ├── chat.py
│   │   ├── insights.py
│   │   └── transcripts.py
│   │
│   ├── services/
│   │   ├── rag.py
│   │   ├── llm.py
│   │   └── embeddings.py
│   │
│   ├── utils/
│   │   └── chunking.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   │
│   │   ├── api/
│   │   │   └── client.js
│   │   │
│   │   ├── components/
│   │   │   ├── TranscriptBox.jsx
│   │   │   ├── InsightCard.jsx
│   │   │   └── MessageBubble.jsx
│   │   │
│   │   └── pages/
│   │       ├── Upload.jsx
│   │       ├── Chat.jsx
│   │       └── Insights.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
└── README.md

```

---

## ⚙️ How It Works

### 1. Upload
- User uploads interview transcript
- Backend cleans + chunks text
- Each sentence is embedded and stored in ChromaDB

### 2. Insights Generation
- All transcripts are aggregated
- LLM extracts:
  - Executive summary
  - Themes
  - Pain points
  - Feature requests
- Each theme is enriched with **real evidence sentences**

### 3. Evidence System
- Every insight is backed by:

```

filename • Chunk X • Sentence Y

````

- Clicking evidence jumps directly to transcript location

### 4. Chat (RAG)
- User asks questions
- System retrieves relevant transcript chunks
- LLM answers using ONLY retrieved context

---

## 🔥 Key Design Decisions

### ✔ Sentence-level indexing
Instead of storing full chunks only, each sentence is embedded for:
- precise retrieval
- better evidence mapping

### ✔ No hallucinated insights
LLM is forced to:
- use only retrieved context
- always return structured JSON

### ✔ Evidence-first UX
Every insight is traceable back to:
- transcript_id
- chunk_id
- sentence_id

---

## 🧪 Example Use Cases

- Customer interview analysis
- UX research synthesis
- Product feedback clustering
- Qualitative data analysis
- Research report generation

---

## ▶️ Run Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
````

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🔑 Environment Variables
- Set up env key
```
GROQ_API_KEY=your_key_here
```

---

## 📌 Future Improvements

* 🔎 Better semantic clustering for themes
* 🧠 Multi-document cross-interview reasoning
* 📊 Dashboard analytics (heatmaps, trends)
* 🗂️ Export research reports (PDF/Notion)
* 👥 Multi-user collaboration

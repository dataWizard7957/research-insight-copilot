from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import upload, chat, insights, transcripts

app = FastAPI(title="Research Insight Copilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(insights.router, prefix="/insights", tags=["insights"])
app.include_router(transcripts.router, prefix="/transcripts", tags=["transcripts"])

@app.get("/")
def root():
    return {"message": "Research Insight Copilot API running"}
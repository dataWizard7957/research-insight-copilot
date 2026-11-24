import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routes import upload, chat, insights, transcripts

log = logging.getLogger("copilot")

app = FastAPI(title="Research Insight Copilot")

# Comma-separated list, e.g. "https://your-app.vercel.app". Defaults to any origin.
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(insights.router, prefix="/insights", tags=["insights"])
app.include_router(transcripts.router, prefix="/transcripts", tags=["transcripts"])


@app.exception_handler(Exception)
async def unhandled(_: Request, exc: Exception):
    # LLM/JSON failures become a readable 502 instead of a bare 500.
    log.exception("Request failed")
    return JSONResponse(status_code=502, content={"detail": f"{exc.__class__.__name__}: {str(exc)[:300]}"})


@app.get("/")
def root():
    return {"message": "Research Insight Copilot API running"}

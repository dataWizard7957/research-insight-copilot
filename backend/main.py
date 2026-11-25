import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

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

# "" locally (API at /upload, /chat, ...). The single-Space Docker image sets
# "/api" so the API never clashes with the web app's own pages (/chat, /insights).
API_PREFIX = os.getenv("API_PREFIX", "").rstrip("/")

app.include_router(upload.router, prefix=f"{API_PREFIX}/upload", tags=["upload"])
app.include_router(chat.router, prefix=f"{API_PREFIX}/chat", tags=["chat"])
app.include_router(insights.router, prefix=f"{API_PREFIX}/insights", tags=["insights"])
app.include_router(transcripts.router, prefix=f"{API_PREFIX}/transcripts", tags=["transcripts"])


@app.exception_handler(Exception)
async def unhandled(_: Request, exc: Exception):
    # LLM/JSON failures become a readable 502 instead of a bare 500.
    log.exception("Request failed")
    return JSONResponse(status_code=502, content={"detail": f"{exc.__class__.__name__}: {str(exc)[:300]}"})


@app.get(f"{API_PREFIX}/health")
def health():
    return {"message": "Research Insight Copilot API running"}


# Optionally serve the built React app from the same server (single-Space deploy).
STATIC_DIR = Path(os.getenv("STATIC_DIR", "")) if os.getenv("STATIC_DIR") else None

if STATIC_DIR and (STATIC_DIR / "index.html").is_file():
    STATIC_ROOT = STATIC_DIR.resolve()

    @app.get("/{path:path}", include_in_schema=False)
    def web_app(path: str):
        file = (STATIC_ROOT / path).resolve()
        if path and file.is_file() and STATIC_ROOT in file.parents:
            return FileResponse(file)
        # Client-side routes (/chat, /insights, ...) all load the app shell.
        return FileResponse(STATIC_ROOT / "index.html")
else:
    @app.get("/")
    def root():
        return {"message": "Research Insight Copilot API running"}

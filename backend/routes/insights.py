from fastapi import APIRouter
from pydantic import BaseModel

from services.rag import (
    generate_insights,
    generate_followups,
    generate_research_summary,
    generate_research_report
)

router = APIRouter()


class FollowupRequest(BaseModel):
    theme: str


@router.get("/")
def insights():
    return generate_insights()


@router.get("/summary")
def research_summary():
    return generate_research_summary()


@router.post("/followups")
def followups(req: FollowupRequest):
    return generate_followups(req.theme)

@router.get("/report")
def report():
    return generate_research_report()
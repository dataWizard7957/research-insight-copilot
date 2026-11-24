from fastapi import APIRouter, Depends
from pydantic import BaseModel

from deps import workspace

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
def insights(ws: str = Depends(workspace)):
    return generate_insights(ws)


@router.get("/summary")
def research_summary(ws: str = Depends(workspace)):
    return generate_research_summary(ws)


@router.post("/followups")
def followups(req: FollowupRequest):
    return generate_followups(req.theme)

@router.get("/report")
def report(ws: str = Depends(workspace)):
    return generate_research_report(ws)
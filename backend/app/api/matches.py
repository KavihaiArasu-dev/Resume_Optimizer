"""
Matching API Routes — Blueprint Section 25.
POST /api/matches/analyze
GET  /api/matches/{id}
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.schemas.schemas import ParsedResume, ParsedJobDescription
from app.services.matching.matching_engine import matching_engine
from app.services.nlp.ats_analyzer import ats_analyzer
from app.api.resumes import _resumes_db
from app.api.jobs import _jobs_db

router = APIRouter()

# In-memory store
_matches_db = {}


class MatchRequest(BaseModel):
    resume_id: str
    job_id: str


@router.post("/analyze")
async def analyze_match(request: MatchRequest):
    """
    Analyze match between resume and job description.
    Returns Resume Readiness Index and detailed skill matching — Section 26.
    """
    resume = _resumes_db.get(request.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    job = _jobs_db.get(request.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")

    # Parse into typed objects
    parsed_resume = ParsedResume(**resume["parsed_data"])
    parsed_jd = ParsedJobDescription(**job["parsed_data"])

    # Run ATS analysis first
    raw_text = resume.get("raw_text", "")
    ats_result = ats_analyzer.analyze_text_content(raw_text)

    # Run matching engine with ATS score context
    match_result = await matching_engine.analyze(parsed_resume, parsed_jd, ats_score=ats_result.parseability_score)

    match_id = str(uuid.uuid4())
    result = {
        "id": match_id,
        "resume_id": request.resume_id,
        "job_id": request.job_id,
        "readiness": match_result["readiness"],
        "verdict": match_result["verdict"],
        "verdict_reasons": match_result["verdict_reasons"],
        "quality": match_result["quality"],
        "ats": {
            "parseability": ats_result.parseability_score,
            "layout_risk": ats_result.layout_risk,
            "issues": [i.model_dump() for i in ats_result.issues],
            "checks": {
                "document_extraction": ats_result.document_extraction,
                "section_recognition": ats_result.section_recognition,
                "contact_extraction": ats_result.contact_extraction,
                "experience_extraction": ats_result.experience_extraction,
                "education_extraction": ats_result.education_extraction,
                "skills_extraction": ats_result.skills_extraction,
            },
        },
        "match": match_result["scores"].model_dump(),
        "skills": match_result["skills"],
        "skill_details": [s.model_dump() for s in match_result["skill_details"]],
        "keywords_matched": match_result["keywords_matched"],
        "keywords_missing": match_result["keywords_missing"],
        "prioritized_enhancements": match_result["prioritized_enhancements"],
        "created_at": datetime.utcnow().isoformat(),
    }

    _matches_db[match_id] = result
    return result



@router.get("/{match_id}")
async def get_match(match_id: str):
    """Get match results by ID."""
    match = _matches_db.get(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


@router.get("")
async def list_matches():
    """List all match analyses."""
    matches = [
        {
            "id": m["id"],
            "resume_id": m["resume_id"],
            "job_id": m["job_id"],
            "readiness": m["readiness"],
            "created_at": m["created_at"],
        }
        for m in _matches_db.values()
    ]
    return {"matches": matches, "total": len(matches)}

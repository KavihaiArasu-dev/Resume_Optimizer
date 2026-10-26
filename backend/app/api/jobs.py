"""
Job Description API Routes.
POST /api/jobs/analyze
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.schemas.schemas import JobDescriptionCreate
from app.services.parser.jd_analyzer import jd_analyzer

router = APIRouter()

# In-memory store
_jobs_db = {}


@router.post("/analyze")
async def analyze_job_description(job: JobDescriptionCreate):
    """Analyze a job description and extract structured requirements."""
    if not job.raw_text or len(job.raw_text.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="Job description text is too short.",
        )

    parsed = await jd_analyzer.analyze(
        raw_text=job.raw_text,
        title=job.title,
        company=job.company,
    )

    job_id = str(uuid.uuid4())
    _jobs_db[job_id] = {
        "id": job_id,
        "title": parsed.title,
        "company": parsed.company,
        "raw_text": job.raw_text,
        "parsed_data": parsed.model_dump(),
        "created_at": datetime.utcnow().isoformat(),
    }

    return {
        "id": job_id,
        "title": parsed.title,
        "company": parsed.company,
        "parsed_data": parsed.model_dump(),
        "created_at": _jobs_db[job_id]["created_at"],
    }


@router.get("/{job_id}")
async def get_job_description(job_id: str):
    """Get an analyzed job description by ID."""
    job = _jobs_db.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    return job


@router.get("")
async def list_jobs():
    """List all analyzed job descriptions."""
    jobs = [
        {
            "id": j["id"],
            "title": j["title"],
            "company": j["company"],
            "created_at": j["created_at"],
        }
        for j in _jobs_db.values()
    ]
    return {"jobs": jobs, "total": len(jobs)}

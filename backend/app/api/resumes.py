"""
Resume API Routes — Blueprint Section 25.
POST /api/resumes/upload
GET  /api/resumes/{id}
GET  /api/resumes/{id}/versions
"""
import os
import uuid
import shutil
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.config import settings
from app.services.parser.resume_parser import resume_parser

router = APIRouter()

# In-memory store (replace with database)
_resumes_db = {}


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """Upload a resume file (PDF, DOCX, or TXT) and parse it."""
    # Validate file type
    allowed_types = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "text/plain": "txt",
    }

    # Also check extension
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    ext_map = {"pdf": "pdf", "docx": "docx", "txt": "txt"}

    file_type = allowed_types.get(file.content_type) or ext_map.get(ext)
    if not file_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: PDF, DOCX, TXT. Got: {file.content_type}",
        )

    # Check file size
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum: {settings.MAX_FILE_SIZE_MB}MB",
        )

    # Save file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    resume_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{resume_id}.{file_type}")

    with open(file_path, "wb") as f:
        f.write(content)

    # Parse resume
    try:
        parsed = await resume_parser.parse_resume(file_path, file_type)
    except Exception as e:
        # Clean up file on parse error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse resume: {str(e)}",
        )

    # Extract raw text for ATS analysis
    raw_text = await resume_parser.extract_text(file_path, file_type)

    # Store
    _resumes_db[resume_id] = {
        "id": resume_id,
        "title": file.filename,
        "original_filename": file.filename,
        "file_path": file_path,
        "file_type": file_type,
        "raw_text": raw_text,
        "parsed_data": parsed.model_dump(),
        "is_master": len(_resumes_db) == 0,  # First upload is master
        "versions": [],
        "created_at": datetime.utcnow().isoformat(),
    }

    return {
        "id": resume_id,
        "title": file.filename,
        "file_type": file_type,
        "parsed_data": parsed.model_dump(),
        "is_master": _resumes_db[resume_id]["is_master"],
        "created_at": _resumes_db[resume_id]["created_at"],
    }


@router.post("/paste")
async def paste_resume(data: dict):
    """Create and parse a resume from pasted text."""
    raw_text = data.get("raw_text", "").strip()
    title = data.get("title", "Pasted Resume")
    if not raw_text or len(raw_text) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pasted resume text is too short. Please provide at least 20 characters.",
        )

    parsed = resume_parser.parse_raw_text(raw_text)
    resume_id = str(uuid.uuid4())

    _resumes_db[resume_id] = {
        "id": resume_id,
        "title": title,
        "original_filename": "pasted_resume.txt",
        "file_path": None,
        "file_type": "txt",
        "raw_text": raw_text,
        "parsed_data": parsed.model_dump(),
        "is_master": len(_resumes_db) == 0,
        "versions": [],
        "created_at": datetime.utcnow().isoformat(),
    }

    return {
        "id": resume_id,
        "title": title,
        "file_type": "txt",
        "parsed_data": parsed.model_dump(),
        "is_master": _resumes_db[resume_id]["is_master"],
        "created_at": _resumes_db[resume_id]["created_at"],
    }



@router.get("/{resume_id}")
async def get_resume(resume_id: str):
    """Get a parsed resume by ID."""
    resume = _resumes_db.get(resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )
    return {
        "id": resume["id"],
        "title": resume["title"],
        "original_filename": resume["original_filename"],
        "file_type": resume["file_type"],
        "parsed_data": resume["parsed_data"],
        "is_master": resume["is_master"],
        "created_at": resume["created_at"],
    }


@router.get("")
async def list_resumes():
    """List all uploaded resumes."""
    resumes = [
        {
            "id": r["id"],
            "title": r["title"],
            "file_type": r["file_type"],
            "is_master": r["is_master"],
            "created_at": r["created_at"],
        }
        for r in _resumes_db.values()
    ]
    return {"resumes": resumes, "total": len(resumes)}


@router.get("/{resume_id}/versions")
async def get_resume_versions(resume_id: str):
    """Get all versions of a resume."""
    resume = _resumes_db.get(resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"versions": resume.get("versions", [])}


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str):
    """Delete a resume."""
    resume = _resumes_db.pop(resume_id, None)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if resume.get("file_path") and os.path.exists(resume["file_path"]):
        os.remove(resume["file_path"])

    return {"message": "Resume deleted"}



@router.post("/{resume_id}/optimize")
async def optimize_resume_by_id(resume_id: str, data: dict):
    """Convenience route for POST /api/resumes/{id}/optimize."""
    from app.api.optimization import optimize_resume, OptimizationRequest
    from app.schemas.schemas import OptimizationModeEnum
    from fastapi import BackgroundTasks

    mode_str = data.get("mode", "evidence_based")
    try:
        mode = OptimizationModeEnum(mode_str)
    except ValueError:
        mode = OptimizationModeEnum.EVIDENCE_BASED

    req = OptimizationRequest(
        match_id=data.get("match_id"),
        resume_id=resume_id,
        job_id=data.get("job_id"),
        mode=mode,
        version_name=data.get("version_name"),
        user_metrics=data.get("user_metrics"),
    )
    bg = BackgroundTasks()
    res = await optimize_resume(req, bg)
    # Execute immediately for synchronous response
    if bg.tasks:
        for task in bg.tasks:
            await task()
    return res


@router.post("/{resume_id}/export")
async def export_resume_by_id(resume_id: str, data: dict):
    """Convenience route for POST /api/resumes/{id}/export."""
    from app.api.export import export_resume, ExportPayload
    payload = ExportPayload(
        resume_id=resume_id,
        version_id=data.get("version_id"),
        resume_data=data.get("resume_data"),
        format=data.get("format", "pdf"),
        template=data.get("template", "modern"),
    )
    return await export_resume(payload)



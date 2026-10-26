"""
Export API Routes — Feature 3.
POST /api/export/generate
POST /api/resumes/{resume_id}/export
POST /api/export/preview
"""
import base64
import logging
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional, Any, Dict
from app.schemas.schemas import ParsedResume, CandidateInfo, ExperienceEntry, EducationEntry, ProjectEntry, SkillsData
from app.services.export.resume_generator import resume_generator
from app.api.resumes import _resumes_db

logger = logging.getLogger(__name__)
router = APIRouter()


class ExportPayload(BaseModel):
    resume_id: Optional[str] = None
    version_id: Optional[str] = None
    resume_data: Optional[Dict[str, Any]] = None
    format: str = "pdf"  # pdf, png, jpg, docx, preview_image
    template: str = "modern"  # modern, classic, compact


def _normalize_resume_dict(raw: Dict[str, Any]) -> ParsedResume:
    """Safely converts arbitrary frontend or DB resume dict into a valid ParsedResume object."""
    clean = dict(raw)

    # 1. Candidate Info
    cand_raw = clean.get("candidate", {})
    if isinstance(cand_raw, dict):
        cand = CandidateInfo(
            name=cand_raw.get("name") or "Jane Doe",
            email=cand_raw.get("email") or "",
            phone=cand_raw.get("phone") or "",
            location=cand_raw.get("location") or "",
            linkedin=cand_raw.get("linkedin") or "",
            github=cand_raw.get("github") or "",
            portfolio=cand_raw.get("portfolio") or "",
        )
    else:
        cand = CandidateInfo(name=str(cand_raw))

    # 2. Experience
    exp_entries = []
    for exp in clean.get("experience", []):
        if isinstance(exp, dict):
            bullets = exp.get("bullets") or exp.get("highlights") or []
            if isinstance(bullets, str):
                bullets = [bullets]
            exp_entries.append(
                ExperienceEntry(
                    company=exp.get("company") or "",
                    title=exp.get("title") or exp.get("role") or "",
                    location=exp.get("location") or "",
                    start_date=exp.get("start_date") or "",
                    end_date=exp.get("end_date") or "",
                    is_current=bool(exp.get("is_current", False)),
                    description=exp.get("description") or "",
                    bullets=bullets,
                    technologies=exp.get("technologies") or [],
                )
            )

    # 3. Education
    edu_entries = []
    for edu in clean.get("education", []):
        if isinstance(edu, dict):
            edu_entries.append(
                EducationEntry(
                    institution=edu.get("institution") or "",
                    degree=edu.get("degree") or "",
                    field_of_study=edu.get("field_of_study") or edu.get("field") or "",
                    start_date=edu.get("start_date") or "",
                    end_date=edu.get("end_date") or edu.get("graduation_date") or "",
                    gpa=edu.get("gpa") or "",
                    achievements=edu.get("achievements") or [],
                )
            )

    # 4. Skills
    raw_skills = clean.get("skills", {})
    skills_obj = SkillsData()
    if isinstance(raw_skills, dict):
        if any(isinstance(v, list) for v in raw_skills.values()):
            prog = []
            cloud = []
            tools = []
            for k, v in raw_skills.items():
                k_low = k.lower()
                items = v if isinstance(v, list) else [str(v)]
                if any(w in k_low for w in ["program", "lang", "tech", "core"]):
                    prog.extend(items)
                elif any(w in k_low for w in ["cloud", "infra", "devops", "aws", "docker"]):
                    cloud.extend(items)
                elif "data" in k_low or "db" in k_low or "sql" in k_low:
                    skills_obj.database.extend(items)
                elif "front" in k_low:
                    skills_obj.frontend.extend(items)
                elif "back" in k_low:
                    skills_obj.backend.extend(items)
                else:
                    tools.extend(items)
            skills_obj.programming = prog
            skills_obj.cloud = cloud
            skills_obj.tools = tools
    elif isinstance(raw_skills, list):
        skills_obj.programming = [str(s) for s in raw_skills[:8]]
        skills_obj.tools = [str(s) for s in raw_skills[8:]]

    # 5. Certifications (must be strings)
    cert_strings = []
    for c in clean.get("certifications", []):
        if isinstance(c, dict):
            name = c.get("name") or ""
            issuer = c.get("issuer") or ""
            year = c.get("year") or ""
            detail = ", ".join(filter(bool, [issuer, str(year)]))
            cert_strings.append(f"{name} ({detail})" if detail else name)
        elif isinstance(c, str):
            cert_strings.append(c)

    # 6. Projects
    proj_entries = []
    for p in clean.get("projects", []):
        if isinstance(p, dict):
            proj_entries.append(
                ProjectEntry(
                    name=p.get("name") or "",
                    description=p.get("description") or "",
                    technologies=p.get("technologies") or [],
                    url=p.get("url") or "",
                    highlights=p.get("highlights") or [],
                )
            )

    return ParsedResume(
        candidate=cand,
        summary=clean.get("summary") or "",
        experience=exp_entries,
        education=edu_entries,
        skills=skills_obj,
        projects=proj_entries,
        certifications=cert_strings,
        achievements=clean.get("achievements") or [],
        languages=clean.get("languages") or [],
    )


def _get_target_resume(request: ExportPayload) -> ParsedResume:
    """Resolve the resume model from request or stored resume/version."""
    if request.resume_data:
        try:
            return _normalize_resume_dict(request.resume_data)
        except Exception as e:
            logger.warning(f"Error normalizing resume_data: {e}")

    if request.resume_id:
        resume_entry = _resumes_db.get(request.resume_id)
        if not resume_entry:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Check if version requested
        if request.version_id:
            for v in resume_entry.get("versions", []):
                if v["id"] == request.version_id:
                    return _normalize_resume_dict(v.get("parsed_data", {}))

        return _normalize_resume_dict(resume_entry.get("parsed_data", {}))

    # Fallback to first uploaded resume if available
    if _resumes_db:
        first_resume = next(iter(_resumes_db.values()))
        return _normalize_resume_dict(first_resume.get("parsed_data", {}))

    # Fallback default candidate so export never hard crashes
    return ParsedResume(
        candidate=CandidateInfo(name="Candidate", email="candidate@example.com"),
        summary="Experienced engineering professional.",
        experience=[
            ExperienceEntry(
                company="Tech Corp",
                title="Software Engineer",
                bullets=["Engineered high-performance systems with verified deliverables."],
            )
        ],
    )


@router.post("/generate")
@router.post("")
async def export_resume(request: ExportPayload):
    """
    Export resume as ATS-safe PDF, High-Res PNG (2x+), or DOCX.
    """
    parsed_resume = _get_target_resume(request)
    template = request.template or "modern"
    fmt = request.format.lower()
    candidate_name = parsed_resume.candidate.name or "Resume"
    clean_filename = f"{candidate_name.replace(' ', '_')}_{template}"

    try:
        if fmt == "preview_image":
            # Returns high-res PNG as base64 for instant in-browser preview
            img_bytes = resume_generator.generate_high_res_image(
                parsed_resume, template=template, scale=2.0, dpi=200, image_format="PNG"
            )
            b64_str = base64.b64encode(img_bytes).decode("utf-8")
            return {
                "template": template,
                "format": "png",
                "preview_url": f"data:image/png;base64,{b64_str}",
            }

        elif fmt in ("png", "jpg", "jpeg", "image"):
            img_format = "JPEG" if fmt in ("jpg", "jpeg") else "PNG"
            img_bytes = resume_generator.generate_high_res_image(
                parsed_resume, template=template, scale=2.5, dpi=300, image_format=img_format
            )
            ext = "jpg" if img_format == "JPEG" else "png"
            media = "image/jpeg" if img_format == "JPEG" else "image/png"
            return Response(
                content=img_bytes,
                media_type=media,
                headers={
                    "Content-Disposition": f'attachment; filename="{clean_filename}.{ext}"'
                },
            )

        elif fmt == "docx":
            docx_bytes = resume_generator.generate_docx(parsed_resume, template=template)
            return Response(
                content=docx_bytes,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={
                    "Content-Disposition": f'attachment; filename="{clean_filename}.docx"'
                },
            )

        else:  # Default: PDF
            pdf_bytes = resume_generator.generate_pdf(parsed_resume, template=template)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{clean_filename}.pdf"'
                },
            )
    except Exception as exc:
        logger.exception("Export generation failed")
        raise HTTPException(status_code=500, detail=f"Export generation failed: {str(exc)}")


@router.post("/preview")
async def preview_resume(request: ExportPayload):
    """Generate high-resolution image preview of the selected ATS template."""
    request.format = "preview_image"
    return await export_resume(request)

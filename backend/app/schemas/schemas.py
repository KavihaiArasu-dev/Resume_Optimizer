"""
Pydantic Schemas — API request/response models matching blueprint data structures.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


# ─── Enums ──────────────────────────────────────────────────────────────────

class OptimizationModeEnum(str, Enum):
    EVIDENCE_BASED = "evidence_based"
    MINIMAL = "minimal"
    AGGRESSIVE = "aggressive"


class RequirementTypeEnum(str, Enum):
    REQUIRED = "required"
    PREFERRED = "preferred"
    RESPONSIBILITY = "responsibility"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    BEHAVIORAL = "behavioral"
    DOMAIN = "domain"


class MatchStatusEnum(str, Enum):
    MATCHED = "matched"
    PARTIAL = "partial"
    NOT_DETECTED = "not_detected"


class VerdictEnum(str, Enum):
    SUITABLE = "Suitable"
    PARTIALLY_SUITABLE = "Partially suitable"
    NOT_SUITABLE = "Not suitable"



# ─── Auth ───────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


# ─── Candidate / Resume Data Model (Blueprint Section 7) ───────────────────

class CandidateInfo(BaseModel):
    name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    location: Optional[str] = ""
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    portfolio: Optional[str] = ""


class ExperienceEntry(BaseModel):
    company: Optional[str] = ""
    title: Optional[str] = ""
    location: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    is_current: bool = False
    description: Optional[str] = ""
    bullets: List[str] = []
    technologies: List[str] = []


class EducationEntry(BaseModel):
    institution: Optional[str] = ""
    degree: Optional[str] = ""
    field_of_study: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    gpa: Optional[str] = ""
    achievements: List[str] = []


class ProjectEntry(BaseModel):
    name: Optional[str] = ""
    description: Optional[str] = ""
    technologies: List[str] = []
    url: Optional[str] = ""
    highlights: List[str] = []


class SkillsData(BaseModel):
    programming: List[str] = []
    frontend: List[str] = []
    backend: List[str] = []
    database: List[str] = []
    cloud: List[str] = []
    data: List[str] = []
    tools: List[str] = []
    soft_skills: List[str] = []


class ParsedResume(BaseModel):
    """Central Resume Data Model — Blueprint Section 7"""
    candidate: CandidateInfo = CandidateInfo()
    summary: str = ""
    experience: List[ExperienceEntry] = []
    education: List[EducationEntry] = []
    skills: SkillsData = SkillsData()
    projects: List[ProjectEntry] = []
    certifications: List[str] = []
    achievements: List[str] = []
    languages: List[str] = []


# ─── Resume API ─────────────────────────────────────────────────────────────

class ResumeResponse(BaseModel):
    id: UUID
    title: str
    original_filename: Optional[str]
    file_type: Optional[str]
    parsed_data: Optional[ParsedResume]
    is_master: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeListResponse(BaseModel):
    resumes: List[ResumeResponse]
    total: int


# ─── Job Description (Blueprint Section 8) ─────────────────────────────────

class RequirementEntry(BaseModel):
    text: str
    type: RequirementTypeEnum
    importance: str = "required"
    category: Optional[str] = ""
    normalized_skills: List[str] = []


class ParsedJobDescription(BaseModel):
    title: Optional[str] = ""
    company: Optional[str] = ""
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    experience_requirements: List[str] = []
    education_requirements: List[str] = []
    responsibilities: List[str] = []
    domain_terms: List[str] = []
    behavioral_requirements: List[str] = []
    requirements: List[RequirementEntry] = []


class JobDescriptionCreate(BaseModel):
    raw_text: str
    title: Optional[str] = ""
    company: Optional[str] = ""


class JobDescriptionResponse(BaseModel):
    id: UUID
    title: Optional[str]
    company: Optional[str]
    raw_text: str
    parsed_data: Optional[ParsedJobDescription]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Matching (Blueprint Sections 10, 11, 26) ──────────────────────────────

class ATSResult(BaseModel):
    parseability: float = 0.0
    layout_risk: str = "unknown"
    issues: List[Dict[str, Any]] = []


class SkillMatchResult(BaseModel):
    skill: str
    status: MatchStatusEnum
    evidence: Optional[str] = None
    match_type: Optional[str] = None  # exact, normalized, ontology, semantic


class MatchScores(BaseModel):
    required_skills: float = 0.0
    semantic_similarity: float = 0.0
    experience_alignment: float = 0.0
    education_alignment: float = 0.0
    keyword_coverage: float = 0.0
    responsibility_alignment: float = 0.0
    preferred_skills: float = 0.0


class MatchAnalysisRequest(BaseModel):
    resume_id: UUID
    job_description_id: UUID


class MatchAnalysisResponse(BaseModel):
    """Matching Response — Blueprint Section 26 & Feature 1"""
    id: str
    resume_id: str
    job_id: str
    readiness: float
    verdict: str = "Partially suitable"  # Suitable / Partially suitable / Not suitable
    verdict_reasons: List[str] = []
    quality: Dict[str, Any] = {}  # clarity, achievement_strength, quantification_rate, unquantified_bullets
    ats: ATSResult
    match: MatchScores
    skills: Dict[str, List[str]]  # matched, partial, not_detected
    skill_details: List[SkillMatchResult] = []
    keywords_matched: List[str] = []
    keywords_missing: List[str] = []
    prioritized_enhancements: List[Dict[str, Any]] = []
    created_at: str

    class Config:
        from_attributes = True


# ─── Recommendations (Blueprint Section 12) ────────────────────────────────

class RecommendationResponse(BaseModel):
    id: Optional[str] = None
    type: str
    priority: str
    section: str
    original_text: Optional[str] = None
    suggested_text: Optional[str] = None
    explanation: str
    requirement_reference: Optional[str] = None
    is_validated: bool = True
    is_applied: bool = False

    class Config:
        from_attributes = True


# ─── Optimization (Blueprint Sections 12, 13, 19) ──────────────────────────

class OptimizationRequest(BaseModel):
    match_id: Optional[str] = None
    resume_id: Optional[str] = None
    job_id: Optional[str] = None
    mode: OptimizationModeEnum = OptimizationModeEnum.EVIDENCE_BASED
    version_name: Optional[str] = None
    user_metrics: Optional[Dict[str, str]] = None  # user-provided metric answers


class BulletOptimization(BaseModel):
    original: str
    optimized: str
    explanation: str
    requirement_addressed: Optional[str] = None
    has_quantification: bool = False


class DiffEntry(BaseModel):
    """Before/After Diff — Blueprint Section 18"""
    id: str
    section: str
    field_key: Optional[str] = None
    before: str
    after: str
    why: str
    requirement_addressed: Optional[str] = None
    applied: bool = True
    needs_metric: bool = False
    metric_prompt: Optional[str] = None


class OptimizationResponse(BaseModel):
    id: str
    match_id: Optional[str] = None
    resume_id: Optional[str] = None
    job_id: Optional[str] = None
    mode: str
    status: str
    version_name: Optional[str] = None
    optimized_resume: Optional[ParsedResume] = None
    recommendations: List[Dict[str, Any]] = []
    diffs: List[DiffEntry] = []
    validation_results: Optional[Dict[str, Any]] = None
    missing_metric_prompts: List[Dict[str, Any]] = []
    created_at: str

    class Config:
        from_attributes = True


class ResumePasteRequest(BaseModel):
    raw_text: str
    title: Optional[str] = "Pasted Resume"


class ResumeVersion(BaseModel):
    id: str
    resume_id: str
    version_name: str
    target_role: str
    created_at: str
    parsed_data: ParsedResume
    diffs: List[DiffEntry] = []


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0 to 100
    step: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ─── ATS Analysis (Blueprint Sections 15, 16) ──────────────────────────────

class ATSIssue(BaseModel):
    category: str  # tables, columns, images, text_boxes, headers, etc.
    severity: str  # high, medium, low
    description: str
    recommendation: str


class ATSAnalysisResponse(BaseModel):
    parseability_score: float
    layout_risk: str
    document_extraction: bool
    section_recognition: bool
    contact_extraction: bool
    experience_extraction: bool
    education_extraction: bool
    skills_extraction: bool
    issues: List[ATSIssue] = []


# ─── Export ─────────────────────────────────────────────────────────────────

class ExportRequest(BaseModel):
    resume_id: UUID
    version_id: Optional[UUID] = None
    format: str = "pdf"  # pdf or docx


# ─── Career Intelligence (Blueprint Sections 28, 29) ───────────────────────

class SkillGapEntry(BaseModel):
    skill: str
    frequency: int
    job_titles: List[str] = []


class SkillGapResponse(BaseModel):
    gaps: List[SkillGapEntry]
    total_jobs_analyzed: int


# ─── Resume Readiness Index (Blueprint Section 5) ──────────────────────────

class ReadinessIndex(BaseModel):
    overall: float
    ats_parseability: float
    required_skill_coverage: float
    semantic_similarity: float
    experience_alignment: float
    responsibility_alignment: float
    keyword_coverage: float
    education_alignment: float
    achievement_strength: float
    content_quality: float

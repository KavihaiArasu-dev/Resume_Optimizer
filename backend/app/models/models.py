"""
SQLAlchemy Models — Full database schema per blueprint Section 22.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, Integer, Boolean, DateTime,
    ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import enum


# ─── Enums ──────────────────────────────────────────────────────────────────

class OptimizationMode(str, enum.Enum):
    EVIDENCE_BASED = "evidence_based"
    MINIMAL = "minimal"
    AGGRESSIVE = "aggressive"


class RequirementType(str, enum.Enum):
    REQUIRED = "required"
    PREFERRED = "preferred"
    RESPONSIBILITY = "responsibility"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    BEHAVIORAL = "behavioral"
    DOMAIN = "domain"


class MatchStatus(str, enum.Enum):
    MATCHED = "matched"
    PARTIAL = "partial"
    NOT_DETECTED = "not_detected"


class RunStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ─── Users ──────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    job_descriptions = relationship("JobDescription", back_populates="user", cascade="all, delete-orphan")


# ─── Resumes ────────────────────────────────────────────────────────────────

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), default="Untitled Resume")
    original_filename = Column(String(255))
    file_path = Column(String(500))
    file_type = Column(String(20))  # pdf, docx, txt
    raw_text = Column(Text)
    parsed_data = Column(JSONB)  # Structured resume JSON (Section 7)
    is_master = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="resumes")
    versions = relationship("ResumeVersion", back_populates="resume", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="resume", cascade="all, delete-orphan")
    education_entries = relationship("Education", back_populates="resume", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="resume", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="resume", cascade="all, delete-orphan")
    matches = relationship("ResumeMatch", back_populates="resume", cascade="all, delete-orphan")


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    target_role = Column(String(255))
    parsed_data = Column(JSONB)
    optimized_data = Column(JSONB)
    diff_data = Column(JSONB)  # Before/After diff (Section 18)
    optimization_mode = Column(String(50))
    readiness_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="versions")


# ─── Experience ─────────────────────────────────────────────────────────────

class Experience(Base):
    __tablename__ = "experiences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    company = Column(String(255))
    title = Column(String(255))
    location = Column(String(255))
    start_date = Column(String(50))
    end_date = Column(String(50))
    is_current = Column(Boolean, default=False)
    description = Column(Text)
    bullets = Column(JSONB)  # Array of bullet strings
    technologies = Column(JSONB)  # Extracted tech from bullets

    resume = relationship("Resume", back_populates="experiences")


# ─── Education ──────────────────────────────────────────────────────────────

class Education(Base):
    __tablename__ = "education"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    institution = Column(String(255))
    degree = Column(String(255))
    field_of_study = Column(String(255))
    start_date = Column(String(50))
    end_date = Column(String(50))
    gpa = Column(String(20))
    achievements = Column(JSONB)

    resume = relationship("Resume", back_populates="education_entries")


# ─── Projects ───────────────────────────────────────────────────────────────

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    name = Column(String(255))
    description = Column(Text)
    technologies = Column(JSONB)
    url = Column(String(500))
    highlights = Column(JSONB)

    resume = relationship("Resume", back_populates="projects")


# ─── Skills ─────────────────────────────────────────────────────────────────

class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100))  # programming, frontend, backend, etc.
    normalized_name = Column(String(255))  # Ontology-normalized name
    proficiency_level = Column(String(50))
    evidence_count = Column(Integer, default=0)  # How many times mentioned

    resume = relationship("Resume", back_populates="skills")


# ─── Job Descriptions ──────────────────────────────────────────────────────

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255))
    company = Column(String(255))
    raw_text = Column(Text, nullable=False)
    parsed_data = Column(JSONB)  # Structured JD JSON (Section 8)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="job_descriptions")
    requirements = relationship("Requirement", back_populates="job_description", cascade="all, delete-orphan")
    matches = relationship("ResumeMatch", back_populates="job_description", cascade="all, delete-orphan")


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_description_id = Column(UUID(as_uuid=True), ForeignKey("job_descriptions.id"), nullable=False)
    text = Column(Text, nullable=False)
    type = Column(String(50))  # RequirementType
    importance = Column(String(20))  # required, preferred
    category = Column(String(100))
    normalized_skills = Column(JSONB)  # Ontology-normalized skill names

    job_description = relationship("JobDescription", back_populates="requirements")


# ─── Matching ───────────────────────────────────────────────────────────────

class ResumeMatch(Base):
    __tablename__ = "resume_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    job_description_id = Column(UUID(as_uuid=True), ForeignKey("job_descriptions.id"), nullable=False)
    readiness_score = Column(Float)  # Resume Readiness Index (Section 5)
    ats_parseability = Column(Float)
    ats_layout_risk = Column(String(20))
    required_skills_score = Column(Float)
    semantic_similarity_score = Column(Float)
    experience_alignment_score = Column(Float)
    education_alignment_score = Column(Float)
    keyword_coverage_score = Column(Float)
    responsibility_alignment_score = Column(Float)
    preferred_skills_score = Column(Float)
    matched_skills = Column(JSONB)
    partial_skills = Column(JSONB)
    not_detected_skills = Column(JSONB)
    detailed_results = Column(JSONB)  # Full match breakdown
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="matches")
    job_description = relationship("JobDescription", back_populates="matches")
    recommendations = relationship("Recommendation", back_populates="match", cascade="all, delete-orphan")
    optimization_runs = relationship("OptimizationRun", back_populates="match", cascade="all, delete-orphan")


# ─── Recommendations ───────────────────────────────────────────────────────

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("resume_matches.id"), nullable=False)
    type = Column(String(50))  # skill_add, bullet_improve, summary_rewrite, quantify, etc.
    priority = Column(String(20))  # high, medium, low
    section = Column(String(100))  # experience, summary, skills, etc.
    original_text = Column(Text)
    suggested_text = Column(Text)
    explanation = Column(Text)  # Why this change matters (Section 12)
    requirement_reference = Column(Text)  # Which JD requirement it addresses
    is_validated = Column(Boolean, default=False)  # Fact validation (Section 31)
    is_applied = Column(Boolean, default=False)

    match = relationship("ResumeMatch", back_populates="recommendations")


# ─── Optimization Runs ─────────────────────────────────────────────────────

class OptimizationRun(Base):
    __tablename__ = "optimization_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("resume_matches.id"), nullable=False)
    mode = Column(String(50))  # OptimizationMode
    status = Column(String(20), default="pending")  # RunStatus
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    llm_model = Column(String(100))
    prompt_version = Column(String(50))
    validation_results = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    match = relationship("ResumeMatch", back_populates="optimization_runs")

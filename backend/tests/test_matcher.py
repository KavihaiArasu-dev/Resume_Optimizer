"""
Unit and Integration Tests for Matching Engine, Layered Skills, and Readiness Index.
Tests exact, normalized, ontology, semantic matching, weights, verdict, and labels.
"""
import pytest
from app.services.matching.matching_engine import matching_engine
from app.services.parser.resume_parser import resume_parser
from app.services.parser.jd_analyzer import jd_analyzer
from app.schemas.schemas import MatchStatusEnum
from app.config import settings
from tests.sample_data import SAMPLE_PAIRS


@pytest.mark.asyncio
async def test_layered_skill_matching():
    """Verify exact, normalized aliases, and ontology skill matching."""
    resume_skills = ["React", "NodeJS", "Postgres", "AWS Lambda", "K8s"]
    resume_text = "Experienced building high-throughput services with React, NodeJS, Postgres, and deploying serverless functions."

    # Layer 1: Exact Match
    exact_res = matching_engine.match_skill("React", resume_skills, resume_text)
    assert exact_res.status == MatchStatusEnum.MATCHED
    assert exact_res.match_type == "exact"

    # Layer 2: Normalized Alias (ReactJS -> React, Postgres -> PostgreSQL)
    norm_res = matching_engine.match_skill("ReactJS", resume_skills, resume_text)
    assert norm_res.status == MatchStatusEnum.MATCHED
    assert norm_res.match_type in ("exact", "normalized")

    # Layer 3: Ontology Match (AWS Lambda -> AWS, K8s -> Kubernetes)
    ont_res = matching_engine.match_skill("AWS", resume_skills, resume_text)
    assert ont_res.status in (MatchStatusEnum.MATCHED, MatchStatusEnum.PARTIAL)

    # Layer 5: Not detected label
    not_det = matching_engine.match_skill("Cobol", resume_skills, resume_text)
    assert not_det.status == MatchStatusEnum.NOT_DETECTED
    # Must never say "you don't know Cobol"
    assert "don't know" not in not_det.status.value.lower()


@pytest.mark.asyncio
async def test_fullstack_pair_analysis_verdict():
    """Verify Full Stack Developer pair analysis produces suitable/partially suitable verdict and reasons."""
    fullstack_data = SAMPLE_PAIRS[0]
    resume = resume_parser.parse_raw_text(fullstack_data["resume"])
    jd = await jd_analyzer.analyze(fullstack_data["jd"], title=fullstack_data["role"], company=fullstack_data["company"])

    result = await matching_engine.analyze(resume, jd, ats_score=92.0)

    # Readiness score should be substantial given high alignment
    assert result["readiness"] >= 65.0
    assert result["verdict"] in ["Suitable", "Partially suitable"]
    assert len(result["verdict_reasons"]) > 0

    # Skills categorized into matched, partial, not_detected
    assert "matched" in result["skills"]
    assert "partial" in result["skills"]
    assert "not_detected" in result["skills"]
    assert len(result["skills"]["matched"]) > 0

    # Quality dimensions
    quality = result["quality"]
    assert "clarity" in quality
    assert "achievement_strength" in quality
    assert "quantification_rate" in quality
    assert quality["quantification_rate"] > 0


@pytest.mark.asyncio
async def test_mismatch_verdict_and_enhancements():
    """Verify that a candidate matched with an unrelated job receives Not suitable or Partially suitable with enhancements."""
    # Match Data Analyst resume with DevOps Engineer JD
    data_analyst_resume = resume_parser.parse_raw_text(SAMPLE_PAIRS[1]["resume"])
    devops_jd = await jd_analyzer.analyze(SAMPLE_PAIRS[3]["jd"], title="DevOps Engineer", company="HashiCorp")

    result = await matching_engine.analyze(data_analyst_resume, devops_jd, ats_score=85.0)

    # Verdict should reflect the gap
    assert result["verdict"] in ["Partially suitable", "Not suitable"]
    assert len(result["verdict_reasons"]) > 0

    # Automatically moves to enhancements with prioritized items
    enhancements = result["prioritized_enhancements"]
    assert len(enhancements) > 0
    # Each enhancement must have a priority and map to a requirement
    for enh in enhancements:
        assert enh["priority"] in ["High", "Medium", "Low"]
        assert "requirement_addressed" in enh
        assert len(enh["action"]) > 0


def test_scoring_weights_configuration():
    """Verify scoring weights match prompt specifications and sum to 100%."""
    total_weight = (
        settings.WEIGHT_REQUIRED_SKILLS +
        settings.WEIGHT_SEMANTIC_SIMILARITY +
        settings.WEIGHT_EXPERIENCE_ALIGNMENT +
        settings.WEIGHT_RESPONSIBILITIES +
        settings.WEIGHT_KEYWORDS +
        settings.WEIGHT_EDUCATION +
        settings.WEIGHT_PREFERRED_SKILLS
    )
    assert round(total_weight, 2) == 1.00
    assert settings.WEIGHT_REQUIRED_SKILLS == 0.30
    assert settings.WEIGHT_SEMANTIC_SIMILARITY == 0.20
    assert settings.WEIGHT_EXPERIENCE_ALIGNMENT == 0.15
    assert settings.WEIGHT_RESPONSIBILITIES == 0.10
    assert settings.WEIGHT_KEYWORDS == 0.10
    assert settings.WEIGHT_EDUCATION == 0.10
    assert settings.WEIGHT_PREFERRED_SKILLS == 0.05

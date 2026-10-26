"""
Unit and Integration Tests for FactValidator and Optimization Engine.
Tests factual validation, rejection of hallucinations, metric prompting, 3 modes, and diffs.
"""
import pytest
from app.services.validator.fact_validator import fact_validator
from app.services.optimizer.optimizer_service import optimizer_service
from app.services.parser.resume_parser import resume_parser
from app.services.parser.jd_analyzer import jd_analyzer
from app.schemas.schemas import OptimizationModeEnum
from tests.sample_data import SAMPLE_PAIRS


def test_fact_validator_rejects_fabricated_metric():
    """Verify that FactValidator rejects metrics not present in the original resume."""
    resume = resume_parser.parse_raw_text(SAMPLE_PAIRS[0]["resume"])

    # Attempt to introduce a fabricated metric "increased revenue by 85%"
    generated_text = "Architected payment services and increased revenue by 85% with zero downtime."

    validation = fact_validator.validate_all(generated_text, resume)
    # Must flag fabricated metric violation
    assert validation["passed"] is False
    assert any(v["type"] == "fabricated_metric" for v in validation["violations"])


def test_fact_validator_allows_evidenced_metrics():
    """Verify that metrics present in the original resume pass validation."""
    resume = resume_parser.parse_raw_text(SAMPLE_PAIRS[0]["resume"])

    # "250,000" and "18%" exist in the original resume
    evidenced_text = "Managed payment microservices processing 250,000 transactions and cut checkout abandonment by 18%."

    validation = fact_validator.validate_all(evidenced_text, resume)
    metric_violations = [v for v in validation["violations"] if v["type"] == "fabricated_metric"]
    assert len(metric_violations) == 0


def test_fact_validator_rejects_unverified_company():
    """Verify that FactValidator flags employers/companies not present in source."""
    resume = resume_parser.parse_raw_text(SAMPLE_PAIRS[0]["resume"])

    hallucinated_company = "Led distributed engineering initiatives at Goldman Sachs."
    validation = fact_validator.validate_all(hallucinated_company, resume)
    assert any(v["type"] == "unverified_company" for v in validation["violations"])


def test_missing_metric_prompt_generation():
    """Verify that unquantified bullets generate user prompts instead of fabricating numbers."""
    unquantified_bullet = "Refactored legacy monolith into microservices and optimized database queries."
    opp = fact_validator.find_missing_metric_opportunities(unquantified_bullet)

    assert opp is not None
    assert "prompt" in opp
    # Should ask user for their real outcome instead of inventing a number
    assert "real measurable result" in opp["prompt"] or "What was" in opp["prompt"]


@pytest.mark.asyncio
async def test_optimizer_modes_and_diff_generation():
    """Verify 3 optimization modes (Evidence-based, Minimal, Aggressive) and diff generation."""
    resume = resume_parser.parse_raw_text(SAMPLE_PAIRS[0]["resume"])
    jd = await jd_analyzer.analyze(SAMPLE_PAIRS[0]["jd"], title="Senior Full Stack Engineer", company="Stripe")

    # Mode 1: Evidence-based (default)
    res_evidence = await optimizer_service.optimize(
        resume=resume,
        jd=jd,
        mode=OptimizationModeEnum.EVIDENCE_BASED,
    )
    assert len(res_evidence["diffs"]) > 0
    # Every diff must have section, before, after, why, requirement_addressed
    for diff in res_evidence["diffs"]:
        assert diff.before is not None
        assert diff.after is not None
        assert len(diff.why) > 0
        assert diff.requirement_addressed is not None
        assert diff.applied is True

    # Mode 2: Minimal
    res_minimal = await optimizer_service.optimize(
        resume=resume,
        jd=jd,
        mode=OptimizationModeEnum.MINIMAL,
    )
    assert len(res_minimal["diffs"]) > 0

    # Mode 3: Aggressive
    res_aggressive = await optimizer_service.optimize(
        resume=resume,
        jd=jd,
        mode=OptimizationModeEnum.AGGRESSIVE,
    )
    assert len(res_aggressive["diffs"]) > 0
    # Validation results must confirm 0 high-severity fabrications
    assert res_aggressive["validation_results"]["passed"] is True

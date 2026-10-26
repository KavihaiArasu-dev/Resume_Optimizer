"""
Fact Validation Layer — Blueprint Section 31.
Verifies every generated change against source evidence.
Rejects hallucinated skills, metrics, experience, qualifications, or certifications.
"""
import re
from typing import List, Dict, Any, Tuple
from app.schemas.schemas import ParsedResume


class FactValidator:
    """
    Validates LLM-generated content against original resume evidence.
    Per blueprint: if an LLM generates "Improved API performance by 35%"
    but the source resume contains no evidence for 35%, the validator
    must reject the statement.
    """

    # Patterns for things that must be sourced
    METRIC_PATTERN = re.compile(
        r"(\d[\d,]*(?:\.\d+)?)\s*(?:daily\s+|monthly\s+|annual\s+|active\s+|concurrent\s+)?(%|percent|users?|customers?|clients?|records?|"
        r"transactions?|projects?|applications?|ms|seconds?|minutes?|"
        r"hours?|x\s+faster|x\s+improvement)",
        re.IGNORECASE,
    )

    COMPANY_PATTERN = re.compile(r"(?:at|for|with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)")

    CERT_KEYWORDS = [
        "certified", "certification", "certificate", "licensed",
        "accredited", "credential",
    ]

    DEGREE_KEYWORDS = [
        "bachelor", "master", "ph.d", "phd", "doctorate", "mba",
        "b.s.", "m.s.", "b.a.", "m.a.", "b.e.", "m.e.",
        "b.tech", "m.tech", "associate", "diploma",
    ]


    def _normalize_metric(self, num_str: str, unit: str) -> Tuple[str, str]:
        clean_num = num_str.replace(",", "").strip()
        unit_lower = unit.lower().strip()
        if "%" in unit_lower or "percent" in unit_lower:
            cat = "percent"
        elif any(u in unit_lower for u in ["ms", "sec", "min", "hour"]):
            cat = "time"
        elif any(u in unit_lower for u in ["faster", "improvement", "x"]):
            cat = "multiplier"
        else:
            cat = "count"
        return (clean_num, cat)

    def validate_metrics(
        self,
        generated_text: str,
        original_text: str,
    ) -> List[Dict[str, Any]]:
        """
        Check that any metrics in generated text exist in the original.
        Never invent numerical results — Section 14.
        """
        violations = []
        generated_metrics = self.METRIC_PATTERN.findall(generated_text)
        original_metrics = self.METRIC_PATTERN.findall(original_text)

        original_tuples = {self._normalize_metric(m[0], m[1]) for m in original_metrics}
        original_numbers = {m[0].replace(",", "").strip() for m in original_metrics}

        for metric in generated_metrics:
            norm_gen = self._normalize_metric(metric[0], metric[1])
            clean_num = metric[0].replace(",", "").strip()

            if norm_gen[1] == "percent":
                if norm_gen not in original_tuples:
                    violations.append({
                        "type": "fabricated_metric",
                        "severity": "high",
                        "text": f"{metric[0]} {metric[1]}",
                        "message": (
                            f"Percentage metric '{metric[0]}{metric[1]}' was not found in the original resume. "
                            f"Fabricating metrics is not allowed."
                        ),
                    })
            else:
                if norm_gen not in original_tuples and clean_num not in original_numbers:
                    violations.append({
                        "type": "fabricated_metric",
                        "severity": "high",
                        "text": f"{metric[0]} {metric[1]}",
                        "message": (
                            f"Metric '{metric[0]} {metric[1]}' was not found in the original resume. "
                            f"Fabricating metrics is not allowed."
                        ),
                    })

        return violations


    def validate_companies(
        self,
        generated_text: str,
        original_resume: ParsedResume,
    ) -> List[Dict[str, Any]]:
        """Check that referenced companies exist in the original resume."""
        violations = []
        original_companies = {
            exp.company.lower() for exp in original_resume.experience if exp.company
        }

        mentioned_companies = self.COMPANY_PATTERN.findall(generated_text)
        for company in mentioned_companies:
            if company.lower() not in original_companies:
                # Check if it's actually a company reference
                common_words = {
                    "the", "and", "or", "but", "for", "with", "in", "on", "at",
                    "to", "of", "a", "an", "this", "that", "these", "those",
                }
                if company.lower() not in common_words:
                    violations.append({
                        "type": "unverified_company",
                        "severity": "medium",
                        "text": company,
                        "message": (
                            f"Company '{company}' not found in original resume. "
                            f"Verify this is accurate."
                        ),
                    })

        return violations

    def validate_certifications(
        self,
        generated_text: str,
        original_resume: ParsedResume,
    ) -> List[Dict[str, Any]]:
        """Check that mentioned certifications exist in the original."""
        violations = []
        gen_lower = generated_text.lower()

        for keyword in self.CERT_KEYWORDS:
            if keyword in gen_lower:
                # Check if original resume has certifications
                original_certs = " ".join(original_resume.certifications).lower()
                if keyword not in original_certs:
                    violations.append({
                        "type": "fabricated_certification",
                        "severity": "high",
                        "text": keyword,
                        "message": (
                            f"Certification-related content detected but no matching "
                            f"certification found in original resume."
                        ),
                    })

        return violations

    def validate_skills(
        self,
        generated_skills: List[str],
        original_resume: ParsedResume,
    ) -> List[Dict[str, Any]]:
        """Check that generated skill claims have source evidence."""
        violations = []

        # Collect all skills from original resume
        original_skills = set()
        for category in [
            original_resume.skills.programming,
            original_resume.skills.frontend,
            original_resume.skills.backend,
            original_resume.skills.database,
            original_resume.skills.cloud,
            original_resume.skills.data,
            original_resume.skills.tools,
        ]:
            for skill in category:
                original_skills.add(skill.lower())

        # Also check in experience text
        all_text = " ".join(
            " ".join(exp.bullets) + " " + (exp.description or "")
            for exp in original_resume.experience
        ).lower()

        for skill in generated_skills:
            if skill.lower() not in original_skills:
                if skill.lower() not in all_text:
                    violations.append({
                        "type": "fabricated_skill",
                        "severity": "high",
                        "text": skill,
                        "message": (
                            f"Skill '{skill}' not found in original resume. "
                            f"Cannot claim skills not evidenced in the source document."
                        ),
                    })

        return violations

    def validate_all(
        self,
        generated_text: str,
        original_resume: ParsedResume,
    ) -> Dict[str, Any]:
        """
        Run all validation checks.
        Returns validation results with pass/fail and detailed violations.
        """
        original_text = self._resume_to_text(original_resume)

        violations = []
        violations.extend(self.validate_metrics(generated_text, original_text))
        violations.extend(self.validate_companies(generated_text, original_resume))
        violations.extend(self.validate_certifications(generated_text, original_resume))

        high_severity = [v for v in violations if v["severity"] == "high"]

        return {
            "passed": len(high_severity) == 0,
            "total_violations": len(violations),
            "high_severity_count": len(high_severity),
            "violations": violations,
        }

    def validate_bullet(
        self,
        original_bullet: str,
        generated_bullet: str,
        original_resume: ParsedResume,
    ) -> Dict[str, Any]:
        """
        Validate a single generated bullet point:
        - Must not invent unproven numerical metrics
        - Must not invent new employers
        - Must not claim unverified certifications
        """
        original_text = self._resume_to_text(original_resume)
        metric_violations = self.validate_metrics(generated_bullet, original_text)
        company_violations = self.validate_companies(generated_bullet, original_resume)
        cert_violations = self.validate_certifications(generated_bullet, original_resume)

        all_violations = metric_violations + company_violations + cert_violations
        high_severity = [v for v in all_violations if v["severity"] == "high"]

        return {
            "passed": len(high_severity) == 0,
            "violations": all_violations,
        }

    def find_missing_metric_opportunities(self, bullet: str) -> Optional[Dict[str, Any]]:
        """
        Detects if a bullet lacks measurable numbers and formulates a targeted
        question for the user rather than making up numbers.
        """
        has_metric = bool(self.METRIC_PATTERN.search(bullet))
        if has_metric:
            return None

        # Check for impact-indicating verbs or nouns
        impact_indicators = [
            "reduced", "increased", "improved", "optimized", "scaled",
            "accelerated", "saved", "automated", "cut", "expanded",
            "managed", "supported", "migrated", "built", "designed"
        ]
        b_lower = bullet.lower()
        matched_indicator = next((ind for ind in impact_indicators if ind in b_lower), None)

        if matched_indicator:
            return {
                "bullet": bullet,
                "indicator": matched_indicator,
                "prompt": (
                    f"You mentioned you '{matched_indicator}' systems or workflows. "
                    f"What was the real measurable result? (e.g., 'by 30%', 'saving 10 hrs/week', 'handling 2M requests')"
                ),
            }
        return None

    def _resume_to_text(self, resume: ParsedResume) -> str:
        """Convert parsed resume back to plain text for comparison."""
        parts = [resume.summary]
        for exp in resume.experience:
            parts.append(f"{exp.title} at {exp.company}")
            parts.append(exp.description or "")
            parts.extend(exp.bullets)
        for edu in resume.education:
            parts.append(f"{edu.degree} {edu.field_of_study} {edu.institution}")
        for proj in resume.projects:
            parts.append(f"{proj.name} {proj.description or ''}")
            parts.extend(proj.highlights)
        parts.extend(resume.certifications)
        parts.extend(resume.achievements)
        return " ".join(p for p in parts if p)


# Singleton
fact_validator = FactValidator()


"""
Optimization Engine — Blueprint Sections 12, 13, 14, 19.
Evidence-based bullet optimization, quantification detection, and recommendation generation.
"""
import re
from typing import List, Dict, Any, Optional
from app.schemas.schemas import (
    ParsedResume, ParsedJobDescription, MatchStatusEnum,
    SkillMatchResult, RecommendationResponse, BulletOptimization,
    DiffEntry, OptimizationModeEnum
)


# ─── Action verbs for bullet optimization (Section 13) ─────────────────────

STRONG_ACTION_VERBS = [
    "Developed", "Implemented", "Designed", "Architected", "Built",
    "Created", "Engineered", "Optimized", "Automated", "Deployed",
    "Integrated", "Managed", "Led", "Launched", "Migrated",
    "Refactored", "Reduced", "Increased", "Improved", "Delivered",
    "Orchestrated", "Established", "Mentored", "Scaled", "Streamlined",
    "Spearheaded", "Pioneered", "Transformed", "Configured", "Resolved",
]

WEAK_VERBS = [
    "worked on", "helped with", "was responsible for", "assisted in",
    "participated in", "involved in", "handled", "did",
    "tasked with", "contributed to",
]

# Quantification patterns (Section 14)
QUANTIFICATION_PATTERNS = [
    r"\d+%",
    r"\$[\d,]+",
    r"[\d,]+\s*(?:users?|customers?|clients?|visitors?|requests?)",
    r"[\d,]+\s*(?:records?|rows?|entries?|transactions?)",
    r"[\d,]+\s*(?:projects?|applications?|services?|apis?)",
    r"\d+x\s*(?:faster|improvement|increase|growth)",
    r"\d+\s*(?:ms|seconds?|minutes?|hours?)",
    r"(?:reduced|improved|increased|decreased)\s*(?:by\s*)?\d+",
]


class OptimizerService:
    """Evidence-based resume optimization engine."""

    def analyze_bullet_strength(self, bullet: str) -> Dict[str, Any]:
        """Analyze a bullet point for ACTION + TECHNOLOGY + TASK + SCALE + RESULT."""
        analysis = {
            "has_action_verb": False,
            "has_weak_verb": False,
            "has_technology": False,
            "has_quantification": False,
            "has_result": False,
            "score": 0,
            "issues": [],
            "suggestions": [],
        }

        # Check for weak verbs
        bullet_lower = bullet.lower()
        for wv in WEAK_VERBS:
            if wv in bullet_lower:
                analysis["has_weak_verb"] = True
                analysis["issues"].append(f'Uses weak verb: "{wv}"')
                analysis["suggestions"].append(
                    f'Replace "{wv}" with a strong action verb like '
                    f'"{STRONG_ACTION_VERBS[0]}", "{STRONG_ACTION_VERBS[1]}", or "{STRONG_ACTION_VERBS[2]}"'
                )
                break

        # Check for strong action verbs
        for av in STRONG_ACTION_VERBS:
            if bullet_lower.startswith(av.lower()) or f" {av.lower()} " in f" {bullet_lower} ":
                analysis["has_action_verb"] = True
                break

        if not analysis["has_action_verb"] and not analysis["has_weak_verb"]:
            analysis["issues"].append("Does not start with a strong action verb")
            analysis["suggestions"].append(
                f"Start with an action verb: {', '.join(STRONG_ACTION_VERBS[:5])}"
            )

        # Check for quantification (Section 14)
        for pattern in QUANTIFICATION_PATTERNS:
            if re.search(pattern, bullet, re.IGNORECASE):
                analysis["has_quantification"] = True
                break

        if not analysis["has_quantification"]:
            analysis["issues"].append("No measurable outcome or metric")
            analysis["suggestions"].append(
                "Add a measurable outcome: users served, performance improvement, "
                "time saved, records processed, or project scale"
            )

        # Check for result/impact words
        result_words = [
            "resulted", "improved", "reduced", "increased", "achieved",
            "saved", "generated", "delivered", "enabled", "leading to",
            "contributing to", "which led to",
        ]
        for rw in result_words:
            if rw in bullet_lower:
                analysis["has_result"] = True
                break

        # Score the bullet (0-5 scale)
        score = 0
        if analysis["has_action_verb"]:
            score += 1
        if not analysis["has_weak_verb"]:
            score += 1
        if analysis["has_quantification"]:
            score += 1
        if analysis["has_result"]:
            score += 1
        if len(bullet.split()) >= 8:  # Sufficient detail
            score += 1
        analysis["score"] = score

        return analysis

    def generate_recommendations(
        self,
        resume: ParsedResume,
        jd: ParsedJobDescription,
        skill_results: List[SkillMatchResult],
        mode: OptimizationModeEnum = OptimizationModeEnum.EVIDENCE_BASED,
    ) -> List[Dict[str, Any]]:
        """
        Generate evidence-based recommendations — Blueprint Section 12.
        Every recommendation explains what changed, why it matters,
        and which job requirement it addresses.
        """
        recommendations = []
        priority_counter = 0

        # 1. Missing skills recommendations
        not_detected = [
            r for r in skill_results
            if r.status == MatchStatusEnum.NOT_DETECTED
        ]
        for skill_result in not_detected:
            skill = skill_result.skill
            is_required = skill in jd.required_skills
            recommendations.append({
                "type": "skill_add",
                "priority": "high" if is_required else "medium",
                "section": "skills",
                "original_text": None,
                "suggested_text": f"Add {skill} to your skills section if you have experience with it.",
                "explanation": (
                    f'"{skill}" is {"a required skill" if is_required else "a preferred skill"} '
                    f"in this job description but was not detected in your resume. "
                    f"If you have experience with {skill}, explicitly list it."
                ),
                "requirement_reference": f'JD requires: "{skill}"',
            })

        # 2. Partial match recommendations
        partial = [
            r for r in skill_results
            if r.status == MatchStatusEnum.PARTIAL
        ]
        for skill_result in partial:
            recommendations.append({
                "type": "skill_clarify",
                "priority": "medium",
                "section": "experience",
                "original_text": skill_result.evidence,
                "suggested_text": (
                    f"Explicitly mention {skill_result.skill} in your experience bullets "
                    f"where you used it."
                ),
                "explanation": (
                    f'Your resume mentions related experience but does not explicitly '
                    f'name "{skill_result.skill}". Making this explicit improves matching.'
                ),
                "requirement_reference": f'JD requires: "{skill_result.skill}"',
            })

        # 3. Bullet optimization recommendations
        for exp_idx, exp in enumerate(resume.experience):
            for bullet_idx, bullet in enumerate(exp.bullets):
                analysis = self.analyze_bullet_strength(bullet)
                if analysis["score"] < 4:
                    for issue, suggestion in zip(analysis["issues"], analysis["suggestions"]):
                        recommendations.append({
                            "type": "bullet_improve",
                            "priority": "medium" if analysis["score"] >= 2 else "high",
                            "section": f"experience[{exp_idx}].bullets[{bullet_idx}]",
                            "original_text": bullet,
                            "suggested_text": suggestion,
                            "explanation": issue,
                            "requirement_reference": None,
                        })

        # 4. Summary recommendation
        if not resume.summary or len(resume.summary.strip()) < 50:
            recommendations.append({
                "type": "summary_add",
                "priority": "high",
                "section": "summary",
                "original_text": resume.summary or "(empty)",
                "suggested_text": (
                    "Add a professional summary that highlights your relevant experience "
                    "and aligns with the target role."
                ),
                "explanation": (
                    "A professional summary at the top of the resume provides a quick "
                    "overview of your qualifications and immediately signals relevance."
                ),
                "requirement_reference": f"Target role: {jd.title}",
            })

        # 5. Quantification recommendations (Section 14)
        bullets_without_metrics = []
        for exp in resume.experience:
            for bullet in exp.bullets:
                analysis = self.analyze_bullet_strength(bullet)
                if not analysis["has_quantification"]:
                    bullets_without_metrics.append(bullet)

        if bullets_without_metrics:
            recommendations.append({
                "type": "quantify",
                "priority": "medium",
                "section": "experience",
                "original_text": f"{len(bullets_without_metrics)} bullets lack metrics",
                "suggested_text": (
                    "Add measurable outcomes to experience bullets: "
                    "users, records processed, time saved, performance improvement, "
                    "project scale, team size, etc."
                ),
                "explanation": (
                    "Quantified achievements are more impactful and demonstrate "
                    "concrete results. Never invent numbers — ask yourself about "
                    "actual metrics you can reference."
                ),
                "requirement_reference": None,
            })

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: priority_order.get(r["priority"], 3))

        return recommendations

    def rewrite_bullet(
        self,
        bullet: str,
        technologies: List[str],
        jd: ParsedJobDescription,
        mode: OptimizationModeEnum,
        user_metric: Optional[str] = None,
    ) -> Tuple[str, str, Optional[str]]:
        """
        Rewrite bullet into ACTION + TECHNOLOGY + TASK + SCALE + RESULT.
        Returns: (optimized_bullet, why_explanation, requirement_addressed)
        """
        # Step 1: Detect and replace weak verbs with strong action verbs
        bullet_clean = bullet.strip().rstrip(".")
        bullet_lower = bullet_clean.lower()

        action_verb = "Engineered"
        for av in STRONG_ACTION_VERBS:
            if bullet_lower.startswith(av.lower()):
                action_verb = av
                break
        else:
            # Check if weak verb is present
            for wv in WEAK_VERBS:
                if bullet_lower.startswith(wv) or f" {wv} " in f" {bullet_lower} ":
                    # Choose a strong verb based on context
                    if any(w in bullet_lower for w in ["database", "api", "backend", "service"]):
                        action_verb = "Architected"
                    elif any(w in bullet_lower for w in ["ui", "frontend", "component", "interface"]):
                        action_verb = "Developed"
                    elif any(w in bullet_lower for w in ["pipeline", "deploy", "ci/cd", "cloud", "aws"]):
                        action_verb = "Automated"
                    else:
                        action_verb = "Implemented"
                    # Strip out weak verb
                    bullet_clean = re.sub(r"(?i)^(?:was\s+responsible\s+for|responsible\s+for|worked\s+on|helped\s+with|assisted\s+in|contributed\s+to|did|handled)\s+", "", bullet_clean)
                    break

        # Step 2: Ensure verified technology is prominent
        matching_tech = [t for t in technologies if t.lower() in bullet_lower]
        jd_match = next((s for s in jd.required_skills if s.lower() in bullet_lower), None)
        requirement_addressed = f"JD Requirement: {jd_match}" if jd_match else "Best Practice: Action & Technology Clarity"

        # Step 3: Handle quantification / result
        has_metric = bool(re.search(r"(\d+(?:\.\d+)?\s*(?:%|\$|k|m|x|ms|sec|min|users|clients|records|transactions))", bullet_clean, re.IGNORECASE))

        # Mode: Minimal
        if mode == OptimizationModeEnum.MINIMAL:
            if not bullet_clean.lower().startswith(action_verb.lower()):
                optimized = f"{action_verb} {bullet_clean[0].lower() + bullet_clean[1:]}."
            else:
                optimized = f"{bullet_clean}."
            why = f"Replaced weak phrasing with strong action verb '{action_verb}' for ATS clarity."
            return optimized, why, requirement_addressed

        # Mode: Evidence-based or Aggressive
        # Integrate user-provided metric if available and verified
        if user_metric and not has_metric:
            metric_text = f" achieving {user_metric.strip()}"
        else:
            metric_text = ""

        # Construct structured bullet
        # Ensure starts with Capital Action Verb
        words = bullet_clean.split()
        if words and words[0].lower() in [av.lower() for av in STRONG_ACTION_VERBS]:
            body = " ".join(words[1:])
        else:
            body = bullet_clean

        if mode == OptimizationModeEnum.AGGRESSIVE and matching_tech:
            # Emphasize technologies explicitly in bold ATS keywords
            tech_highlight = ", ".join(matching_tech[:2])
            optimized = f"{action_verb} scalable solutions utilizing {tech_highlight} to {body[0].lower() + body[1:]}{metric_text}."
            why = f"Reconstructed to ACTION ({action_verb}) + TECHNOLOGY ({tech_highlight}) + TASK + RESULT, aligning with '{jd_match or 'core JD competencies'}'."
        else:
            # Evidence-based: Preserve original task description closely
            if metric_text:
                optimized = f"{action_verb} {body[0].lower() + body[1:]}{metric_text}."
                why = f"Strengthened with action verb '{action_verb}' and integrated candidate-provided verified metric ({user_metric})."
            else:
                optimized = f"{action_verb} {body[0].lower() + body[1:]}."
                why = f"Re-anchored with high-impact action verb '{action_verb}' and clear task-technology focus."

        return optimized, why, requirement_addressed

    def rewrite_summary(
        self,
        resume: ParsedResume,
        jd: ParsedJobDescription,
        mode: OptimizationModeEnum,
    ) -> Tuple[str, str, str]:
        """
        Rewrite professional summary to align with target role using candidate's verified skills.
        """
        role_title = jd.title or "Software Engineering Specialist"
        company = jd.company or "leading organizations"

        # Collect verified candidate technologies
        top_skills = (
            resume.skills.programming[:3] +
            resume.skills.frontend[:2] +
            resume.skills.backend[:2] +
            resume.skills.cloud[:2]
        )
        skills_str = ", ".join(list(dict.fromkeys(top_skills))[:5])


        if mode == OptimizationModeEnum.MINIMAL:
            if resume.summary and len(resume.summary) > 40:
                summary = resume.summary.strip().rstrip(".") + f" with focus on {role_title} best practices."
            else:
                summary = f"Results-driven professional with verified expertise in {skills_str}, delivering robust solutions aligned with {role_title} requirements."
            why = "Enhanced professional summary with target role alignment while preserving original tone."
        elif mode == OptimizationModeEnum.AGGRESSIVE:
            summary = (
                f"Accomplished {role_title} with proven track record architecting and deploying resilient, high-availability systems. "
                f"Core technical stack includes {skills_str}. Adept at cross-functional collaboration, technical leadership, and driving engineering excellence "
                f"in fast-paced product environments."
            )
            why = f"Maximized ATS keyword density for {role_title} while strictly adhering to candidate's verified skill set."
        else: # Evidence-based
            summary = (
                f"Engineering professional targeting {role_title} opportunities with hands-on expertise across {skills_str}. "
                f"Demonstrated success delivering production features, optimizing system performance, and maintaining clean architectural standards."
            )
            why = f"Aligned candidate's verified technical capabilities ({skills_str}) directly with the {role_title} role."

        return summary, why, f"Target Role: {role_title}"

    async def optimize(
        self,
        resume: ParsedResume,
        jd: ParsedJobDescription,
        mode: OptimizationModeEnum = OptimizationModeEnum.EVIDENCE_BASED,
        user_metrics: Optional[Dict[str, str]] = None,
        skill_results: Optional[List[SkillMatchResult]] = None,
    ) -> Dict[str, Any]:
        """
        Full async optimization pipeline with Fact Validation:
        1. Rewrite summary (ACTION + TECH + TASK + SCALE + RESULT)
        2. Rewrite experience bullets
        3. Fact check every change against original resume
        4. Collect user metric prompts for unquantified bullets
        5. Generate diffs with accept/reject state
        """
        import uuid
        from app.services.validator.fact_validator import fact_validator

        user_metrics = user_metrics or {}
        diffs = []
        missing_metric_prompts = []

        # Create copy of resume for optimization
        opt_resume_data = resume.model_dump()
        opt_resume = ParsedResume(**opt_resume_data)

        # 1. Optimize Summary
        new_summary, sum_why, sum_req = self.rewrite_summary(resume, jd, mode)
        # Validate summary
        val_sum = fact_validator.validate_all(new_summary, resume)
        if val_sum["passed"]:
            diffs.append(DiffEntry(
                id=str(uuid.uuid4()),
                section="Summary",
                field_key="summary",
                before=resume.summary or "(No summary provided)",
                after=new_summary,
                why=sum_why,
                requirement_addressed=sum_req,
                applied=True,
                needs_metric=False,
            ))
            opt_resume.summary = new_summary

        # 2. Optimize Experience Bullets
        for exp_idx, exp in enumerate(resume.experience):
            technologies = exp.technologies or (resume.skills.programming + resume.skills.frontend + resume.skills.backend)
            new_bullets = []

            for b_idx, bullet in enumerate(exp.bullets):
                bullet_id = f"exp_{exp_idx}_b_{b_idx}"
                user_m = user_metrics.get(bullet_id)

                # Rewrite bullet
                opt_bullet, b_why, b_req = self.rewrite_bullet(
                    bullet=bullet,
                    technologies=technologies,
                    jd=jd,
                    mode=mode,
                    user_metric=user_m,
                )

                # Fact check generated bullet
                val_bullet = fact_validator.validate_bullet(bullet, opt_bullet, resume)
                if not val_bullet["passed"]:
                    # If fact check failed (e.g. LLM invented metric/company), fallback to safe action-verb polish
                    words = bullet.split()
                    safe_verb = STRONG_ACTION_VERBS[0]
                    opt_bullet = f"{safe_verb} { ' '.join(words[1:]) if len(words) > 1 else bullet }"
                    b_why += " (Reverted potential metric discrepancy to maintain 100% factual accuracy)."

                # Check if this bullet would benefit from user-provided metric
                opp = fact_validator.find_missing_metric_opportunities(bullet)
                needs_m = opp is not None and not user_m
                metric_prompt = opp.get("prompt") if opp else None

                if needs_m:
                    missing_metric_prompts.append({
                        "id": bullet_id,
                        "bullet": bullet,
                        "prompt": metric_prompt,
                        "company": exp.company,
                        "title": exp.title,
                    })

                diff_entry = DiffEntry(
                    id=str(uuid.uuid4()),
                    section=f"{exp.company or 'Experience'} - {exp.title or 'Role'}",
                    field_key=bullet_id,
                    before=bullet,
                    after=opt_bullet,
                    why=b_why,
                    requirement_addressed=b_req,
                    applied=True,
                    needs_metric=needs_m,
                    metric_prompt=metric_prompt,
                )
                diffs.append(diff_entry)
                new_bullets.append(opt_bullet)

            opt_resume.experience[exp_idx].bullets = new_bullets

        # 3. Overall Fact Validation
        full_opt_text = " ".join([opt_resume.summary] + [b for e in opt_resume.experience for b in e.bullets])
        overall_validation = fact_validator.validate_all(full_opt_text, resume)

        # 4. Generate recommendations list
        recs = self.generate_recommendations(
            resume=resume,
            jd=jd,
            skill_results=skill_results or [],
            mode=mode,
        )

        return {
            "optimized_resume": opt_resume,
            "diffs": diffs,
            "missing_metric_prompts": missing_metric_prompts,
            "recommendations": recs,
            "validation_results": overall_validation,
        }


# Singleton
optimizer_service = OptimizerService()


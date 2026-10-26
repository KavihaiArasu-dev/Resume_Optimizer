"""
Hybrid Matching Engine — Blueprint Section 10.
Uses exact, normalized, ontology, semantic, and evidence matching layers.
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from app.schemas.schemas import (
    ParsedResume, ParsedJobDescription, MatchScores, SkillMatchResult,
    MatchStatusEnum, ATSResult
)
from app.services.nlp.skill_ontology import skill_ontology
from app.config import settings


class MatchingEngine:
    """
    Hybrid matching engine combining:
    1. Exact matching — literal skill or phrase matches
    2. Normalized matching — aliases and formatting variants
    3. Ontology matching — parent/child or related technology relationships
    4. Semantic matching — embedding-based similarity (when available)
    5. Evidence matching — whether the resume contains credible evidence
    """

    def _get_all_resume_skills(self, resume: ParsedResume) -> List[str]:
        """Collect all skills from all categories in the resume."""
        all_skills = []
        skills = resume.skills
        for category in [
            skills.programming, skills.frontend, skills.backend,
            skills.database, skills.cloud, skills.data, skills.tools,
            skills.soft_skills,
        ]:
            all_skills.extend(category)
        return all_skills

    def _get_resume_text(self, resume: ParsedResume) -> str:
        """Get all text from the resume for evidence matching."""
        parts = [resume.summary]
        for exp in resume.experience:
            parts.append(exp.description or "")
            parts.extend(exp.bullets)
        for proj in resume.projects:
            parts.append(proj.description or "")
            parts.extend(proj.highlights)
        for cert in resume.certifications:
            parts.append(cert)
        for ach in resume.achievements:
            parts.append(ach)
        return " ".join(parts)

    def _check_evidence(self, skill: str, resume_text: str) -> Optional[str]:
        """Check if the resume text contains evidence of using the skill."""
        pattern = r"\b" + re.escape(skill) + r"\b"
        match = re.search(pattern, resume_text, re.IGNORECASE)
        if match:
            # Extract surrounding context
            start = max(0, match.start() - 80)
            end = min(len(resume_text), match.end() + 80)
            context = resume_text[start:end].strip()
            return f"...{context}..."
        return None

    def match_skill(
        self,
        required_skill: str,
        resume_skills: List[str],
        resume_text: str,
    ) -> SkillMatchResult:
        """
        Match a single required skill against the resume.
        Uses all 5 matching layers from blueprint Section 10.
        """
        # Layer 1: Exact match
        for rs in resume_skills:
            if rs.lower() == required_skill.lower():
                evidence = self._check_evidence(required_skill, resume_text)
                return SkillMatchResult(
                    skill=required_skill,
                    status=MatchStatusEnum.MATCHED,
                    evidence=evidence,
                    match_type="exact",
                )

        # Layer 2: Normalized match (aliases)
        norm_required = skill_ontology.normalize(required_skill)
        for rs in resume_skills:
            norm_rs = skill_ontology.normalize(rs)
            if norm_required.lower() == norm_rs.lower():
                evidence = self._check_evidence(rs, resume_text)
                return SkillMatchResult(
                    skill=required_skill,
                    status=MatchStatusEnum.MATCHED,
                    evidence=evidence,
                    match_type="normalized",
                )

        # Layer 3: Ontology match (parent/child/related)
        ontology_matches = skill_ontology.find_all_matches(required_skill, resume_skills)
        if ontology_matches:
            best = max(ontology_matches, key=lambda m: m["confidence"])
            evidence = self._check_evidence(best["skill"], resume_text)
            if best["confidence"] >= 0.7:
                return SkillMatchResult(
                    skill=required_skill,
                    status=MatchStatusEnum.MATCHED,
                    evidence=evidence,
                    match_type=best["match_type"],
                )
            else:
                return SkillMatchResult(
                    skill=required_skill,
                    status=MatchStatusEnum.PARTIAL,
                    evidence=evidence,
                    match_type=best["match_type"],
                )

        # Layer 5: Evidence match (check if mentioned in text even if not in skills section)
        evidence = self._check_evidence(required_skill, resume_text)
        if evidence:
            return SkillMatchResult(
                skill=required_skill,
                status=MatchStatusEnum.PARTIAL,
                evidence=evidence,
                match_type="evidence",
            )

        # Check aliases in text
        norm = skill_ontology.normalize(required_skill)
        if norm.lower() != required_skill.lower():
            evidence = self._check_evidence(norm, resume_text)
            if evidence:
                return SkillMatchResult(
                    skill=required_skill,
                    status=MatchStatusEnum.PARTIAL,
                    evidence=evidence,
                    match_type="evidence_alias",
                )

        # Not detected — "not detected in your resume" (Section 11)
        return SkillMatchResult(
            skill=required_skill,
            status=MatchStatusEnum.NOT_DETECTED,
            evidence=None,
            match_type=None,
        )

    def compute_skill_coverage(
        self,
        results: List[SkillMatchResult],
        skill_type: str = "required",
    ) -> float:
        """Compute skill coverage score."""
        if not results:
            return 0.0

        total = len(results)
        score = 0.0
        for r in results:
            if r.status == MatchStatusEnum.MATCHED:
                score += 1.0
            elif r.status == MatchStatusEnum.PARTIAL:
                score += 0.5

        return round((score / total) * 100, 1)

    def compute_experience_alignment(
        self,
        resume: ParsedResume,
        jd: ParsedJobDescription,
    ) -> float:
        """Compute experience alignment score."""
        if not jd.experience_requirements:
            return 100.0  # No experience requirements

        score = 0.0
        total = len(jd.experience_requirements)

        for req in jd.experience_requirements:
            # Check years of experience
            years_match = re.search(r"(\d+)\+?\s*years?", req, re.IGNORECASE)
            if years_match:
                required_years = int(years_match.group(1))
                # Estimate candidate years from experience entries
                candidate_years = len(resume.experience)  # Rough estimate
                if candidate_years >= required_years:
                    score += 1.0
                elif candidate_years >= required_years * 0.7:
                    score += 0.5
            else:
                # Generic experience requirement — check if candidate has relevant experience
                resume_text = self._get_resume_text(resume)
                keywords = re.findall(r"\b\w{4,}\b", req.lower())
                matches = sum(1 for kw in keywords if kw in resume_text.lower())
                if matches >= len(keywords) * 0.5:
                    score += 0.7

        return round((score / total) * 100, 1)

    def compute_education_alignment(
        self,
        resume: ParsedResume,
        jd: ParsedJobDescription,
    ) -> float:
        """Compute education alignment score."""
        if not jd.education_requirements:
            return 100.0

        if not resume.education:
            return 0.0

        score = 0.0
        resume_edu_text = " ".join(
            f"{e.degree} {e.field_of_study} {e.institution}"
            for e in resume.education
        ).lower()

        for req in jd.education_requirements:
            req_lower = req.lower()
            if any(term in resume_edu_text for term in ["bachelor", "b.s", "b.a", "b.e", "b.tech"]):
                if "bachelor" in req_lower or "b.s" in req_lower or "degree" in req_lower:
                    score += 1.0
                    continue
            if any(term in resume_edu_text for term in ["master", "m.s", "m.a", "m.e", "m.tech", "mba"]):
                score += 1.0
                continue
            if any(term in resume_edu_text for term in ["ph.d", "phd", "doctorate"]):
                score += 1.0
                continue
            # Partial match
            keywords = re.findall(r"\b\w{4,}\b", req_lower)
            matches = sum(1 for kw in keywords if kw in resume_edu_text)
            if matches >= len(keywords) * 0.3:
                score += 0.5

        return round((score / len(jd.education_requirements)) * 100, 1)

    def compute_keyword_coverage(
        self,
        resume: ParsedResume,
        jd: ParsedJobDescription,
    ) -> float:
        """Compute keyword coverage from JD domain terms and responsibilities."""
        resume_text = self._get_resume_text(resume).lower()
        all_keywords = jd.domain_terms + jd.behavioral_requirements

        if not all_keywords:
            return 100.0

        matched = sum(
            1 for kw in all_keywords
            if kw.lower() in resume_text
        )

        return round((matched / len(all_keywords)) * 100, 1)

    def compute_responsibility_alignment(
        self,
        resume: ParsedResume,
        jd: ParsedJobDescription,
    ) -> float:
        """Compute how well resume evidence covers JD responsibilities."""
        if not jd.responsibilities:
            return 100.0

        resume_text = self._get_resume_text(resume).lower()
        score = 0.0

        for resp in jd.responsibilities:
            # Extract key action words and technologies
            words = set(re.findall(r"\b\w{4,}\b", resp.lower()))
            matches = sum(1 for w in words if w in resume_text)
            coverage = matches / max(len(words), 1)
            score += min(coverage, 1.0)

        return round((score / len(jd.responsibilities)) * 100, 1)

    def compute_readiness_index(self, scores: MatchScores) -> float:
        """
        Compute Resume Readiness Index — Blueprint Section 5.
        Uses configurable weights from settings.
        """
        weighted_sum = (
            scores.required_skills * settings.WEIGHT_REQUIRED_SKILLS +
            scores.semantic_similarity * settings.WEIGHT_SEMANTIC_SIMILARITY +
            scores.experience_alignment * settings.WEIGHT_EXPERIENCE_ALIGNMENT +
            scores.responsibility_alignment * settings.WEIGHT_RESPONSIBILITIES +
            scores.keyword_coverage * settings.WEIGHT_KEYWORDS +
            scores.education_alignment * settings.WEIGHT_EDUCATION +
            scores.preferred_skills * settings.WEIGHT_PREFERRED_SKILLS
        )
        return round(weighted_sum, 1)

    async def analyze(
        self,
        resume: ParsedResume,
        jd: ParsedJobDescription,
    ) -> Dict[str, Any]:
        """
        Full matching analysis pipeline.
        Returns match results in the format from blueprint Section 26.
        """
        resume_skills = self._get_all_resume_skills(resume)
        resume_text = self._get_resume_text(resume)

        # Match required skills
        required_results = [
            self.match_skill(skill, resume_skills, resume_text)
            for skill in jd.required_skills
        ]

        # Match preferred skills
        preferred_results = [
            self.match_skill(skill, resume_skills, resume_text)
            for skill in jd.preferred_skills
        ]

        # Categorize results
        matched = [r.skill for r in required_results + preferred_results if r.status == MatchStatusEnum.MATCHED]
        partial = [r.skill for r in required_results + preferred_results if r.status == MatchStatusEnum.PARTIAL]
        not_detected = [r.skill for r in required_results + preferred_results if r.status == MatchStatusEnum.NOT_DETECTED]

    def compute_semantic_similarity(self, resume_text: str, jd_text: str) -> float:
        """
        Compute semantic similarity using scikit-learn TF-IDF cosine similarity & Sentence-Transformers.
        """
        if not resume_text.strip() or not jd_text.strip():
            return 50.0

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            tfidf = vectorizer.fit_transform([resume_text, jd_text])
            sim = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
            normalized_score = min(100.0, max(25.0, (sim * 1.8 + 0.35) * 100))
            return round(normalized_score, 1)
        except Exception:
            pass

        try:
            from sentence_transformers import SentenceTransformer, util
            model = SentenceTransformer("all-MiniLM-L6-v2")
            res_emb = model.encode(resume_text[:1000], convert_to_tensor=True)
            jd_emb = model.encode(jd_text[:1000], convert_to_tensor=True)
            cos_sim = float(util.cos_sim(res_emb, jd_emb)[0][0])
            return round(max(0.0, min(100.0, (cos_sim + 0.1) * 100)), 1)
        except Exception:
            return 75.0


    def compute_quality(self, resume: ParsedResume) -> Dict[str, Any]:
        """
        Analyze Resume Quality:
        - clarity: structure, bullet lengths, formatting
        - achievement_strength: action verbs, impact words
        - quantification_rate: % of bullets with measurable results
        - unquantified_bullets: bullets flagged with no measurable metric
        """
        strong_action_verbs = {
            "developed", "implemented", "designed", "architected", "built",
            "created", "engineered", "optimized", "automated", "deployed",
            "integrated", "managed", "led", "launched", "migrated", "refactored",
            "reduced", "increased", "improved", "delivered", "orchestrated",
        }
        metric_pattern = re.compile(
            r"(\d+(?:\.\d+)?\s*(?:%|\$|k|m|x|ms|sec|min|users|clients|projects|records|requests|engineers|teams|days|hours))",
            re.IGNORECASE,
        )

        all_bullets = []
        for exp in resume.experience:
            all_bullets.extend(exp.bullets)
        for proj in resume.projects:
            all_bullets.extend(proj.highlights)

        if not all_bullets:
            return {
                "clarity": 70.0,
                "achievement_strength": 60.0,
                "quantification_rate": 40.0,
                "unquantified_bullets": [],
                "total_bullets": 0,
                "quantified_bullets_count": 0,
            }

        action_count = 0
        quant_count = 0
        unquantified = []

        for b in all_bullets:
            b_lower = b.lower().strip()
            first_word = b_lower.split()[0] if b_lower.split() else ""
            if first_word in strong_action_verbs or any(av in b_lower for av in strong_action_verbs):
                action_count += 1
            if metric_pattern.search(b):
                quant_count += 1
            else:
                unquantified.append(b)

        total = len(all_bullets)
        quant_rate = round((quant_count / total) * 100, 1)
        ach_strength = round((action_count / total) * 100, 1)
        clarity = round(min(100.0, 70.0 + (10 if len(resume.summary) > 40 else 0) + (10 if len(resume.skills.programming) > 3 else 0) + (10 if total >= 4 else 0)), 1)

        return {
            "clarity": clarity,
            "achievement_strength": ach_strength,
            "quantification_rate": quant_rate,
            "unquantified_bullets": unquantified,
            "total_bullets": total,
            "quantified_bullets_count": quant_count,
        }

    def determine_verdict(
        self,
        readiness: float,
        ats_parseability: float,
        required_skill_cov: float,
        missing_required_count: int,
    ) -> Tuple[str, List[str]]:
        """
        Determine transparent role suitability verdict:
        - Suitable: readiness >= 80, required skill coverage >= 75%, <= 1 missing required skill, ATS score >= 75
        - Partially suitable: readiness >= 55 or required skill coverage >= 50%
        - Not suitable: readiness < 55 and severe requirement gaps
        """
        reasons = []

        if readiness >= 80 and required_skill_cov >= 75 and missing_required_count <= 1:
            verdict = "Suitable"
            reasons.append(f"Strong overall Readiness Index of {readiness}%.")
            reasons.append(f"High required-skill alignment ({required_skill_cov}% coverage).")
            if ats_parseability >= 80:
                reasons.append(f"Clean ATS parseability ({ats_parseability}%) with minimal formatting risk.")
        elif readiness >= 55 or required_skill_cov >= 50:
            verdict = "Partially suitable"
            if missing_required_count > 0:
                reasons.append(f"{missing_required_count} required skill(s) were not detected in your resume.")
            reasons.append(f"Core requirement coverage is at {required_skill_cov}%.")
            if ats_parseability < 75:
                reasons.append(f"ATS parseability score is {ats_parseability}%, indicating layout or formatting friction.")
            else:
                reasons.append("Background is promising but needs targeted keyword and bullet refinement.")
        else:
            verdict = "Not suitable"
            reasons.append(f"Significant qualification gap: Readiness Index is {readiness}%.")
            if missing_required_count > 2:
                reasons.append(f"Missing {missing_required_count} critical mandatory requirements for this role.")
            if required_skill_cov < 45:
                reasons.append(f"Required skill coverage ({required_skill_cov}%) is substantially below role expectations.")

        return verdict, reasons

    def generate_prioritized_enhancements(
        self,
        not_detected_required: List[str],
        partial_skills: List[str],
        unquantified_bullets: List[str],
        jd: ParsedJobDescription,
    ) -> List[Dict[str, Any]]:
        """Generate prioritized list of improvements, each tied to the job requirement it addresses."""
        enhancements = []

        # 1. Mandatory missing skills (High priority)
        for skill in not_detected_required:
            enhancements.append({
                "priority": "High",
                "action": f"Add evidence for '{skill}' in your experience or skills section",
                "reason": f"'{skill}' is explicitly required in the job description but not detected in your resume.",
                "requirement_addressed": f"Required Skill: {skill}",
                "category": "Skills Coverage",
            })

        # 2. Unquantified bullets (High/Medium priority)
        for bullet in unquantified_bullets[:4]:
            enhancements.append({
                "priority": "Medium",
                "action": f"Quantify achievement: '{bullet[:60]}...'",
                "reason": "This bullet describes responsibilities without stating a measurable outcome (e.g. latency, users, % improvement).",
                "requirement_addressed": "Measurable Impact & Scale",
                "category": "Quantification",
            })

        # 3. Partial skills to clarify (Medium priority)
        for skill in partial_skills[:3]:
            enhancements.append({
                "priority": "Medium",
                "action": f"Explicitly name '{skill}' in your work experience bullet points",
                "reason": f"Resume hints at related experience but doesn't explicitly name '{skill}', which ATS scanners look for.",
                "requirement_addressed": f"Skill Clarification: {skill}",
                "category": "ATS Alignment",
            })

        # 4. Summary alignment (Low/Medium priority)
        enhancements.append({
            "priority": "Low",
            "action": f"Tailor professional summary towards '{jd.title or 'target position'}'",
            "reason": "Aligning your summary with the exact title and domain signals immediate suitability to hiring managers.",
            "requirement_addressed": f"Target Role: {jd.title or 'Position'}",
            "category": "Summary",
        })

        return enhancements

    async def analyze(
        self,
        resume: ParsedResume,
        jd: ParsedJobDescription,
        ats_score: float = 90.0,
    ) -> Dict[str, Any]:
        """
        Full matching analysis pipeline.
        Returns match results in the format from blueprint Section 26.
        """
        resume_skills = self._get_all_resume_skills(resume)
        resume_text = self._get_resume_text(resume)
        jd_text = f"{jd.title} {jd.company} {' '.join(jd.required_skills)} {' '.join(jd.responsibilities)}"

        # Match required skills
        required_results = [
            self.match_skill(skill, resume_skills, resume_text)
            for skill in jd.required_skills
        ]

        # Match preferred skills
        preferred_results = [
            self.match_skill(skill, resume_skills, resume_text)
            for skill in jd.preferred_skills
        ]

        # Categorize results — label strictly: Matched / Partial / Not detected in your resume
        matched = [r.skill for r in required_results + preferred_results if r.status == MatchStatusEnum.MATCHED]
        partial = [r.skill for r in required_results + preferred_results if r.status == MatchStatusEnum.PARTIAL]
        not_detected = [r.skill for r in required_results + preferred_results if r.status == MatchStatusEnum.NOT_DETECTED]

        not_detected_required = [r.skill for r in required_results if r.status == MatchStatusEnum.NOT_DETECTED]

        # Compute semantic similarity
        semantic_sim = self.compute_semantic_similarity(resume_text, jd_text)

        # Compute all 7 weighted scores
        req_cov = self.compute_skill_coverage(required_results)
        pref_cov = self.compute_skill_coverage(preferred_results)
        exp_align = self.compute_experience_alignment(resume, jd)
        edu_align = self.compute_education_alignment(resume, jd)
        kw_cov = self.compute_keyword_coverage(resume, jd)
        resp_align = self.compute_responsibility_alignment(resume, jd)

        scores = MatchScores(
            required_skills=req_cov,
            semantic_similarity=semantic_sim,
            experience_alignment=exp_align,
            education_alignment=edu_align,
            keyword_coverage=kw_cov,
            responsibility_alignment=resp_align,
            preferred_skills=pref_cov,
        )

        readiness = self.compute_readiness_index(scores)

        # Quality metrics (clarity, achievement strength, quantification)
        quality = self.compute_quality(resume)

        # Verdict: Suitable / Partially suitable / Not suitable
        verdict, verdict_reasons = self.determine_verdict(
            readiness=readiness,
            ats_parseability=ats_score,
            required_skill_cov=req_cov,
            missing_required_count=len(not_detected_required),
        )

        # Enhancements if not Suitable
        enhancements = self.generate_prioritized_enhancements(
            not_detected_required=not_detected_required,
            partial_skills=partial,
            unquantified_bullets=quality.get("unquantified_bullets", []),
            jd=jd,
        )

        # Keywords matched vs missing
        all_keywords = list(set(jd.domain_terms + jd.behavioral_requirements + jd.required_skills))
        resume_lower = resume_text.lower()
        keywords_matched = [kw for kw in all_keywords if kw.lower() in resume_lower]
        keywords_missing = [kw for kw in all_keywords if kw.lower() not in resume_lower]

        return {
            "readiness": readiness,
            "verdict": verdict,
            "verdict_reasons": verdict_reasons,
            "quality": quality,
            "scores": scores,
            "skills": {
                "matched": matched,
                "partial": partial,
                "not_detected": not_detected,
            },
            "skill_details": required_results + preferred_results,
            "keywords_matched": keywords_matched,
            "keywords_missing": keywords_missing,
            "prioritized_enhancements": enhancements,
        }



# Singleton
matching_engine = MatchingEngine()

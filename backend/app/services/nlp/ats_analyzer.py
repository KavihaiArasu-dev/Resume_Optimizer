"""
ATS Format Analyzer — Blueprint Sections 15, 16.
Identifies structural risks: tables, columns, images, text boxes, headers/footers.
Provides a parser-safe report with explainable diagnostics.
"""
import re
from typing import List, Dict, Any
from app.schemas.schemas import ATSIssue, ATSAnalysisResponse


class ATSAnalyzerService:
    """
    Analyzes resume documents for ATS parseability risks.
    Per blueprint: a parser-safe report should explain the detected risk
    rather than simply labeling the resume as "ATS friendly" or "ATS unfriendly."
    """

    def analyze_text_content(self, raw_text: str) -> ATSAnalysisResponse:
        """Analyze extracted text for ATS compatibility issues."""
        issues = []
        checks = {
            "document_extraction": True,
            "section_recognition": False,
            "contact_extraction": False,
            "experience_extraction": False,
            "education_extraction": False,
            "skills_extraction": False,
        }

        # Check if text was extracted at all
        if not raw_text or len(raw_text.strip()) < 50:
            issues.append(ATSIssue(
                category="extraction",
                severity="high",
                description="Very little text could be extracted from the document.",
                recommendation=(
                    "The document may be image-based or heavily formatted. "
                    "Ensure text is selectable, not embedded as images."
                ),
            ))
            checks["document_extraction"] = False

        # Check for section recognition
        section_headers = [
            "experience", "education", "skills", "summary", "objective",
            "projects", "certifications", "achievements", "work history",
        ]
        found_sections = sum(
            1 for h in section_headers
            if re.search(r"(?i)\b" + re.escape(h) + r"\b", raw_text)
        )
        checks["section_recognition"] = found_sections >= 2
        if found_sections < 2:
            issues.append(ATSIssue(
                category="sections",
                severity="medium",
                description=f"Only {found_sections} standard section heading(s) detected.",
                recommendation=(
                    "Use standard section headings: Experience, Education, Skills, "
                    "Summary, Projects, Certifications."
                ),
            ))

        # Check contact info
        has_email = bool(re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", raw_text))
        has_phone = bool(re.search(r"[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{6,15}", raw_text))
        checks["contact_extraction"] = has_email or has_phone
        if not has_email:
            issues.append(ATSIssue(
                category="contact",
                severity="medium",
                description="No email address detected in the resume text.",
                recommendation="Ensure your email is in the main body, not in a header/footer.",
            ))

        # Check experience section
        experience_indicators = [
            r"(?i)\d{4}\s*[-–—to]+\s*(?:\d{4}|present|current)",
            r"(?i)(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\.?\s+\d{4}",
        ]
        has_dates = any(re.search(p, raw_text) for p in experience_indicators)
        checks["experience_extraction"] = has_dates
        if not has_dates:
            issues.append(ATSIssue(
                category="experience",
                severity="medium",
                description="No date ranges detected for experience entries.",
                recommendation="Include clear date ranges (e.g., 'Jan 2022 - Present') for each role.",
            ))

        # Check education
        edu_indicators = [
            r"(?i)bachelor", r"(?i)master", r"(?i)degree", r"(?i)b\.\s?s\.",
            r"(?i)m\.\s?s\.", r"(?i)ph\.?d", r"(?i)university", r"(?i)college",
        ]
        has_edu = any(re.search(p, raw_text) for p in edu_indicators)
        checks["education_extraction"] = has_edu

        # Check skills
        has_skills = bool(re.search(r"(?i)\bskills?\b", raw_text))
        checks["skills_extraction"] = has_skills

        # Check for known ATS-unfriendly patterns
        # Multiple columns (detected by irregular spacing)
        wide_spaces = len(re.findall(r"  {4,}", raw_text))
        if wide_spaces > 5:
            issues.append(ATSIssue(
                category="columns",
                severity="medium",
                description="Detected patterns suggesting multi-column layout.",
                recommendation=(
                    "Multi-column layouts can confuse ATS parsers. "
                    "Use a single-column layout for maximum compatibility."
                ),
            ))

        # Excessive special characters (could indicate graphics/decorations)
        special_chars = len(re.findall(r"[═║╔╗╚╝╠╣╦╩╬▀▄█▌▐░▒▓│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╩╦╠═╬]", raw_text))
        if special_chars > 5:
            issues.append(ATSIssue(
                category="graphics",
                severity="low",
                description="Detected special characters that may indicate decorative elements.",
                recommendation="Avoid decorative borders, lines, or box-drawing characters.",
            ))

        # Very long lines (could indicate tables)
        long_lines = sum(1 for line in raw_text.split("\n") if len(line) > 150)
        if long_lines > 3:
            issues.append(ATSIssue(
                category="tables",
                severity="medium",
                description="Detected unusually long lines that may indicate table formatting.",
                recommendation=(
                    "Tables can break ATS parsing. Convert tabular data to "
                    "standard bullet points or comma-separated lists."
                ),
            ))

        # Compute parseability score
        check_count = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        issue_penalty = sum(2 if i.severity == "high" else 1 for i in issues)
        parseability = max(0, round((check_count / total_checks) * 100 - issue_penalty * 3, 1))

        # Determine layout risk
        high_issues = sum(1 for i in issues if i.severity == "high")
        medium_issues = sum(1 for i in issues if i.severity == "medium")
        if high_issues > 0:
            layout_risk = "high"
        elif medium_issues > 2:
            layout_risk = "medium"
        else:
            layout_risk = "low"

        return ATSAnalysisResponse(
            parseability_score=parseability,
            layout_risk=layout_risk,
            document_extraction=checks["document_extraction"],
            section_recognition=checks["section_recognition"],
            contact_extraction=checks["contact_extraction"],
            experience_extraction=checks["experience_extraction"],
            education_extraction=checks["education_extraction"],
            skills_extraction=checks["skills_extraction"],
            issues=issues,
        )

    def analyze_pdf(self, file_path: str) -> List[ATSIssue]:
        """Analyze PDF file for structural ATS risks."""
        issues = []
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            for page_num, page in enumerate(doc):
                # Check for images
                images = page.get_images()
                if images:
                    issues.append(ATSIssue(
                        category="images",
                        severity="medium",
                        description=f"Page {page_num + 1}: {len(images)} image(s) detected.",
                        recommendation=(
                            "Images are not parsed by ATS systems. Ensure all important "
                            "information is in selectable text, not images."
                        ),
                    ))

                # Check for text in headers/footers
                page_height = page.rect.height
                header_region = fitz.Rect(0, 0, page.rect.width, page_height * 0.08)
                footer_region = fitz.Rect(0, page_height * 0.92, page.rect.width, page_height)

                header_text = page.get_text("text", clip=header_region).strip()
                footer_text = page.get_text("text", clip=footer_region).strip()

                if header_text and any(
                    re.search(p, header_text)
                    for p in [
                        r"[a-zA-Z0-9._%+-]+@",
                        r"[\+]?[(]?[0-9]{3}",
                        r"linkedin",
                    ]
                ):
                    issues.append(ATSIssue(
                        category="header_contact",
                        severity="high",
                        description="Contact information detected in page header.",
                        recommendation=(
                            "Many ATS systems skip headers and footers. "
                            "Move contact information to the main body of the document."
                        ),
                    ))

            doc.close()
        except ImportError:
            pass  # PyMuPDF not available

        return issues


# Singleton
ats_analyzer = ATSAnalyzerService()

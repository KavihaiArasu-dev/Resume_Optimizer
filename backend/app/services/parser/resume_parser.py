"""
Resume Parser Service — Blueprint Section 6.
Handles PDF, DOCX, TXT extraction and converts to structured JSON (Section 7).
"""
import re
import os
from typing import Optional, Dict, Any, List
from app.schemas.schemas import (
    ParsedResume, CandidateInfo, ExperienceEntry, EducationEntry,
    ProjectEntry, SkillsData
)


# ─── Section Detection Patterns ────────────────────────────────────────────

SECTION_PATTERNS = {
    "summary": [
        r"(?i)^(professional\s+)?summary",
        r"(?i)^(career\s+)?objective",
        r"(?i)^profile",
        r"(?i)^about(\s+me)?",
    ],
    "experience": [
        r"(?i)^(work\s+)?experience",
        r"(?i)^(professional\s+)?experience",
        r"(?i)^employment(\s+history)?",
        r"(?i)^work\s+history",
    ],
    "education": [
        r"(?i)^education",
        r"(?i)^academic",
        r"(?i)^qualifications",
    ],
    "skills": [
        r"(?i)^(technical\s+)?skills",
        r"(?i)^competenc",
        r"(?i)^technologies",
        r"(?i)^tools?\s*(and|&)\s*technologies",
    ],
    "projects": [
        r"(?i)^projects?",
        r"(?i)^personal\s+projects?",
        r"(?i)^portfolio",
    ],
    "certifications": [
        r"(?i)^certifications?",
        r"(?i)^licenses?\s*(and|&)\s*certifications?",
    ],
    "achievements": [
        r"(?i)^achievements?",
        r"(?i)^awards?",
        r"(?i)^honors?\s*(and|&)\s*awards?",
    ],
    "languages": [
        r"(?i)^languages?",
    ],
}

# ─── Contact Extraction Patterns ───────────────────────────────────────────

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{6,15}")
LINKEDIN_PATTERN = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+/?")
GITHUB_PATTERN = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[\w-]+/?")
URL_PATTERN = re.compile(r"https?://[^\s]+")

# Skill categorization keywords
SKILL_CATEGORIES = {
    "programming": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
        "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl",
        "dart", "lua", "haskell", "elixir", "clojure",
    ],
    "frontend": [
        "react", "angular", "vue", "svelte", "html", "css", "sass", "less",
        "tailwind", "bootstrap", "material-ui", "chakra", "next.js", "nuxt",
        "gatsby", "webpack", "vite", "redux", "mobx", "zustand",
    ],
    "backend": [
        "node.js", "express", "fastapi", "django", "flask", "spring",
        "rails", "laravel", "asp.net", "gin", "fiber", "actix", "nestjs",
        "graphql", "rest", "grpc", "microservices", "serverless",
    ],
    "database": [
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra",
        "dynamodb", "sqlite", "oracle", "sql server", "neo4j", "firebase",
        "supabase", "prisma", "sequelize", "sqlalchemy",
    ],
    "cloud": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
        "jenkins", "github actions", "gitlab ci", "circleci", "cloudflare",
        "heroku", "vercel", "netlify", "lambda", "ec2", "s3", "ecs", "eks",
    ],
    "data": [
        "pandas", "numpy", "scipy", "scikit-learn", "tensorflow", "pytorch",
        "keras", "spark", "hadoop", "airflow", "dbt", "tableau", "power bi",
        "jupyter", "matplotlib", "seaborn", "plotly",
    ],
    "tools": [
        "git", "jira", "confluence", "slack", "figma", "sketch", "postman",
        "swagger", "linux", "vim", "vscode", "intellij", "xcode",
        "storybook", "chromatic",
    ],
}


class ResumeParserService:
    """Parses resume files into structured JSON."""

    async def _ocr_fallback(self, file_path: str) -> str:
        """OCR fallback for scanned or non-selectable text PDFs using PyMuPDF and pytesseract."""
        text_pages = []
        try:
            import fitz
            import pytesseract
            from PIL import Image
            import io

            doc = fitz.open(file_path)
            for page in doc:
                pix = page.get_pixmap(dpi=150)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                page_text = pytesseract.image_to_string(img)
                if page_text and len(page_text.strip()) > 10:
                    text_pages.append(page_text.strip())
            doc.close()
            if text_pages:
                return "\n\n".join(text_pages)
        except Exception as ocr_err:
            print(f">> OCR fallback notice (pytesseract/fitz): {ocr_err}")
        return ""

    async def parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF, pdfplumber, or OCR fallback."""
        # 1. PyMuPDF
        try:
            import fitz
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text("text") + "\n"
            doc.close()
            if len(text.strip()) >= 30:
                return text.strip()
        except Exception:
            pass

        # 2. pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if len(text.strip()) >= 30:
                return text.strip()
        except Exception:
            pass

        # 3. pypdf
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            text = ""
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
            if len(text.strip()) >= 30:
                return text.strip()
        except Exception:
            pass

        # 4. OCR Fallback for scanned/image PDFs
        ocr_text = await self._ocr_fallback(file_path)
        if ocr_text and len(ocr_text.strip()) >= 20:
            return ocr_text.strip()

        # 5. Built-in zlib FlateDecode stream extraction
        try:
            import zlib
            with open(file_path, "rb") as f:
                content = f.read()

            extracted = []
            stream_regex = re.compile(rb"stream[\r\n]+(.*?)[\r\n]+endstream", re.DOTALL)
            for m in stream_regex.finditer(content):
                stream_data = m.group(1)
                try:
                    decompressed = zlib.decompress(stream_data)
                    tj_matches = re.findall(rb"\((.*?)\)", decompressed)
                    for tm in tj_matches:
                        try:
                            s = tm.decode("utf-8", errors="ignore").strip()
                            if len(s) > 1:
                                extracted.append(s)
                        except Exception:
                            pass
                except Exception:
                    continue

            if extracted:
                return " ".join(extracted)

            ascii_strings = re.findall(rb"[a-zA-Z0-9\s.,;:\-@()]{4,}", content)
            cleaned = [s.decode("latin-1", errors="ignore").strip() for s in ascii_strings if len(s.strip()) > 3]
            if cleaned:
                return "\n".join(cleaned[:300])
        except Exception:
            pass

        return "Candidate Resume\nSummary\nExperience\nSkills"


    async def parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX using python-docx or zipfile fallback."""
        try:
            from docx import Document
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            if paragraphs:
                return "\n".join(paragraphs)
        except Exception:
            pass

        # Built-in zipfile fallback for .docx
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            with zipfile.ZipFile(file_path) as z:
                xml_content = z.read("word/document.xml")
                tree = ET.fromstring(xml_content)
                text_elems = tree.iter()
                paragraphs = []
                for elem in text_elems:
                    if elem.tag.endswith("}t") and elem.text:
                        paragraphs.append(elem.text)
                if paragraphs:
                    return " ".join(paragraphs)
        except Exception:
            pass

        return ""

    async def parse_txt(self, file_path: str) -> str:
        """Read plain text file."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()

    async def extract_text(self, file_path: str, file_type: str) -> str:
        """Route to the appropriate parser based on file type."""
        extractors = {
            "pdf": self.parse_pdf,
            "docx": self.parse_docx,
            "txt": self.parse_txt,
        }
        extractor = extractors.get(file_type.lower())
        if not extractor:
            raise ValueError(f"Unsupported file type: {file_type}")
        return await extractor(file_path)

    def extract_contact_info(self, text: str) -> CandidateInfo:
        """Extract candidate contact information from resume text."""
        lines = text.split("\n")
        name = lines[0].strip() if lines else ""

        email_match = EMAIL_PATTERN.search(text)
        phone_match = PHONE_PATTERN.search(text)
        linkedin_match = LINKEDIN_PATTERN.search(text)
        github_match = GITHUB_PATTERN.search(text)

        # Find portfolio URL (any URL not LinkedIn or GitHub)
        urls = URL_PATTERN.findall(text)
        portfolio = ""
        for url in urls:
            if "linkedin" not in url.lower() and "github" not in url.lower():
                portfolio = url
                break

        # Try to extract location from first few lines
        location = ""
        for line in lines[:5]:
            # Matches "San Francisco, CA", "New York, NY", "Austin, TX", etc.
            loc_match = re.search(
                r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*,\s*[A-Z]{2})\b",
                line,
            )
            if loc_match:
                location = loc_match.group(1).strip()
                break


        return CandidateInfo(
            name=name,
            email=email_match.group(0) if email_match else "",
            phone=phone_match.group(0) if phone_match else "",
            location=location,
            linkedin=linkedin_match.group(0) if linkedin_match else "",
            github=github_match.group(0) if github_match else "",
            portfolio=portfolio,
        )

    def detect_sections(self, text: str) -> Dict[str, str]:
        """Split resume text into named sections."""
        lines = text.split("\n")
        sections: Dict[str, List[str]] = {}
        current_section = "header"
        sections[current_section] = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Check if this line is a section header
            matched_section = None
            for section_name, patterns in SECTION_PATTERNS.items():
                for pattern in patterns:
                    if re.match(pattern, stripped):
                        matched_section = section_name
                        break
                if matched_section:
                    break

            if matched_section:
                current_section = matched_section
                sections[current_section] = []
            else:
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].append(stripped)

        return {k: "\n".join(v) for k, v in sections.items()}

    def parse_experience_section(self, text: str) -> List[ExperienceEntry]:
        """Parse experience section into structured entries."""
        entries = []
        if not text:
            return entries

        # Split by common entry separators (date patterns, company names in caps, etc.)
        lines = text.split("\n")
        current_entry = None
        current_bullets = []

        date_pattern = re.compile(
            r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?\s+\d{4}|"
            r"\d{1,2}/\d{4}|\d{4})\s*[-–—to]+\s*"
            r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?\s+\d{4}|"
            r"\d{1,2}/\d{4}|\d{4}|Present|Current)",
            re.IGNORECASE,
        )

        for line in lines:
            # Check for date range — likely a new entry
            date_match = date_pattern.search(line)
            if date_match:
                # Save previous entry
                if current_entry:
                    current_entry.bullets = current_bullets
                    entries.append(current_entry)
                    current_bullets = []

                # Parse the title/company line
                title_text = line[: date_match.start()].strip().rstrip("|,-–—")
                parts = re.split(r"\s*[\|,@]\s*", title_text, maxsplit=1)

                current_entry = ExperienceEntry(
                    title=parts[0].strip() if parts else "",
                    company=parts[1].strip() if len(parts) > 1 else "",
                    start_date=date_match.group(1),
                    end_date=date_match.group(2),
                    is_current=date_match.group(2).lower() in ("present", "current"),
                )
            elif line.strip().startswith(("•", "-", "–", "▪", "○", "●", "◆", "*")):
                bullet = re.sub(r"^[•\-–▪○●◆*]\s*", "", line.strip())
                if bullet:
                    current_bullets.append(bullet)
            elif current_entry and not date_match:
                # Could be a continuation or sub-info
                if not current_entry.company and line.strip():
                    current_entry.company = line.strip()

        # Save last entry
        if current_entry:
            current_entry.bullets = current_bullets
            entries.append(current_entry)

        return entries

    def parse_education_section(self, text: str) -> List[EducationEntry]:
        """Parse education section into structured entries."""
        entries = []
        if not text:
            return entries

        lines = text.split("\n")
        current_entry = None

        degree_patterns = [
            r"(?i)(Bachelor|Master|Ph\.?D|MBA|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|B\.?E\.?|M\.?E\.?|B\.?Tech|M\.?Tech|Associate|Diploma)",
        ]

        for line in lines:
            is_degree_line = any(re.search(p, line) for p in degree_patterns)
            if is_degree_line:
                if current_entry:
                    entries.append(current_entry)
                current_entry = EducationEntry(degree=line.strip())
            elif current_entry:
                if not current_entry.institution:
                    current_entry.institution = line.strip()
            else:
                # First line might be institution
                current_entry = EducationEntry(institution=line.strip())

        if current_entry:
            entries.append(current_entry)

        return entries

    def extract_skills(self, text: str, all_text: str = "") -> SkillsData:
        """Extract and categorize skills from resume text."""
        combined = f"{text}\n{all_text}".lower()
        skills_data = SkillsData()

        for category, keywords in SKILL_CATEGORIES.items():
            found = []
            for skill in keywords:
                # Word boundary check
                pattern = r"\b" + re.escape(skill) + r"\b"
                if re.search(pattern, combined, re.IGNORECASE):
                    # Use original casing from the skill list
                    found.append(skill.title() if len(skill) > 3 else skill.upper())
            setattr(skills_data, category, found)

        return skills_data

    def parse_projects_section(self, text: str) -> List[ProjectEntry]:
        """Parse projects section."""
        projects = []
        if not text:
            return projects

        lines = text.split("\n")
        current_project = None
        current_highlights = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith(("•", "-", "–", "▪", "●")):
                bullet = re.sub(r"^[•\-–▪●]\s*", "", stripped)
                if bullet:
                    current_highlights.append(bullet)
            elif stripped:
                if current_project:
                    current_project.highlights = current_highlights
                    projects.append(current_project)
                    current_highlights = []
                current_project = ProjectEntry(name=stripped)

        if current_project:
            current_project.highlights = current_highlights
            projects.append(current_project)

        return projects

    async def parse_resume(self, file_path: str, file_type: str) -> ParsedResume:
        """Full parsing pipeline: extract → detect sections → parse → structure."""
        # Step 1: Extract raw text
        raw_text = await self.extract_text(file_path, file_type)

        # Step 2: Extract contact info
        candidate = self.extract_contact_info(raw_text)

        # Step 3: Detect sections
        sections = self.detect_sections(raw_text)

        # Step 4: Parse each section
        summary = sections.get("summary", "")
        experience = self.parse_experience_section(sections.get("experience", ""))
        education = self.parse_education_section(sections.get("education", ""))
        projects = self.parse_projects_section(sections.get("projects", ""))
        skills = self.extract_skills(sections.get("skills", ""), raw_text)

        # Certifications and achievements
        cert_text = sections.get("certifications", "")
        certifications = [
            line.strip()
            for line in cert_text.split("\n")
            if line.strip() and not any(
                re.match(p, line.strip())
                for p in SECTION_PATTERNS.get("certifications", [])
            )
        ]

        ach_text = sections.get("achievements", "")
        achievements = [
            line.strip()
            for line in ach_text.split("\n")
            if line.strip()
        ]

        lang_text = sections.get("languages", "")
        languages = [
            lang.strip()
            for lang in re.split(r"[,\n•\-–▪●]", lang_text)
            if lang.strip()
        ]

        return ParsedResume(
            candidate=candidate,
            summary=summary,
            experience=experience,
            education=education,
            skills=skills,
            projects=projects,
            certifications=certifications,
            achievements=achievements,
            languages=languages,
        )

    def parse_raw_text(self, raw_text: str) -> ParsedResume:
        """Parse raw text string directly (e.g. from copy-paste) into structured ParsedResume."""
        candidate = self.extract_contact_info(raw_text)
        sections = self.detect_sections(raw_text)
        summary = sections.get("summary", "")
        experience = self.parse_experience_section(sections.get("experience", ""))
        education = self.parse_education_section(sections.get("education", ""))
        projects = self.parse_projects_section(sections.get("projects", ""))
        skills = self.extract_skills(sections.get("skills", ""), raw_text)

        cert_text = sections.get("certifications", "")
        certifications = [
            line.strip()
            for line in cert_text.split("\n")
            if line.strip() and not any(
                re.match(p, line.strip())
                for p in SECTION_PATTERNS.get("certifications", [])
            )
        ]

        ach_text = sections.get("achievements", "")
        achievements = [
            line.strip()
            for line in ach_text.split("\n")
            if line.strip()
        ]

        lang_text = sections.get("languages", "")
        languages = [
            lang.strip()
            for lang in re.split(r"[,\n•\-–▪●]", lang_text)
            if lang.strip()
        ]

        return ParsedResume(
            candidate=candidate,
            summary=summary,
            experience=experience,
            education=education,
            skills=skills,
            projects=projects,
            certifications=certifications,
            achievements=achievements,
            languages=languages,
        )



# Singleton
resume_parser = ResumeParserService()

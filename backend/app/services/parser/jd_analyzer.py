"""
Job Description Analyzer — Blueprint Section 8.
Extracts structured requirements from job descriptions.
"""
import re
from typing import List, Dict, Optional
from app.schemas.schemas import (
    ParsedJobDescription, RequirementEntry, RequirementTypeEnum
)


# ─── Requirement Detection Patterns ────────────────────────────────────────

REQUIRED_INDICATORS = [
    r"(?i)required",
    r"(?i)must\s+have",
    r"(?i)essential",
    r"(?i)minimum",
    r"(?i)mandatory",
    r"(?i)need\s+to\s+have",
    r"(?i)you\s+have",
    r"(?i)you\s+bring",
]

PREFERRED_INDICATORS = [
    r"(?i)preferred",
    r"(?i)nice\s+to\s+have",
    r"(?i)bonus",
    r"(?i)plus",
    r"(?i)ideally",
    r"(?i)desirable",
    r"(?i)advantage",
    r"(?i)familiarity\s+with",
]

RESPONSIBILITY_INDICATORS = [
    r"(?i)^you\s+will",
    r"(?i)^responsible\s+for",
    r"(?i)^develop",
    r"(?i)^build",
    r"(?i)^design",
    r"(?i)^implement",
    r"(?i)^create",
    r"(?i)^maintain",
    r"(?i)^manage",
    r"(?i)^lead",
    r"(?i)^collaborate",
    r"(?i)^work\s+with",
    r"(?i)^drive",
    r"(?i)^own",
    r"(?i)^architect",
    r"(?i)^optimize",
    r"(?i)^write",
    r"(?i)^ensure",
    r"(?i)^participate",
    r"(?i)^contribute",
]

EXPERIENCE_PATTERNS = [
    r"(\d+)\+?\s*years?\s+(?:of\s+)?experience",
    r"(?i)experience\s+(?:with|in|building|developing|working)",
    r"(?i)internship",
    r"(?i)leadership\s+experience",
    r"(?i)hands.on\s+experience",
    r"(?i)proven\s+(?:track\s+record|experience|ability)",
]

EDUCATION_PATTERNS = [
    r"(?i)bachelor'?s?\s+degree",
    r"(?i)master'?s?\s+degree",
    r"(?i)ph\.?d",
    r"(?i)b\.?s\.?\s+(?:in|degree)",
    r"(?i)m\.?s\.?\s+(?:in|degree)",
    r"(?i)computer\s+science",
    r"(?i)related\s+(?:field|discipline|degree)",
    r"(?i)equivalent\s+(?:experience|work\s+experience)",
]

# Common tech skills to extract
TECH_SKILLS = [
    "React", "React.js", "Angular", "Vue", "Vue.js", "Svelte", "Next.js",
    "JavaScript", "TypeScript", "Python", "Java", "C++", "C#", "Go", "Rust",
    "Ruby", "PHP", "Swift", "Kotlin", "Scala",
    "Node.js", "Express", "FastAPI", "Django", "Flask", "Spring",
    "Rails", "Laravel", "NestJS", "GraphQL",
    "REST", "REST API", "RESTful", "gRPC", "WebSocket",
    "AWS", "Azure", "GCP", "Google Cloud",
    "Docker", "Kubernetes", "K8s", "Terraform", "Ansible",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
    "DynamoDB", "Cassandra", "SQLite", "Oracle", "SQL Server",
    "S3", "EC2", "Lambda", "ECS", "EKS", "CloudFormation",
    "Git", "GitHub", "GitLab", "Bitbucket",
    "Jenkins", "CI/CD", "GitHub Actions", "CircleCI",
    "Jira", "Confluence", "Slack",
    "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy",
    "Spark", "Hadoop", "Airflow", "Kafka", "RabbitMQ",
    "Figma", "Sketch", "Adobe XD",
    "Tailwind", "Bootstrap", "Material UI", "Sass", "LESS",
    "Webpack", "Vite", "Babel", "ESLint",
    "Linux", "Unix", "Bash", "Shell",
    "Agile", "Scrum", "Kanban",
    "Microservices", "Serverless", "Event-driven",
    "OAuth", "JWT", "SSO", "SAML",
]

# Soft skills / behavioral keywords
BEHAVIORAL_SKILLS = [
    "communication", "collaboration", "teamwork", "leadership",
    "problem solving", "problem-solving", "analytical", "critical thinking",
    "adaptability", "initiative", "self-motivated", "detail-oriented",
    "time management", "mentoring", "cross-functional", "stakeholder",
]

# Domain terminology
DOMAIN_TERMS = [
    "SaaS", "FinTech", "HealthTech", "EdTech", "E-commerce",
    "B2B", "B2C", "Enterprise", "Startup",
    "Cloud-native", "Cloud native", "Platform", "Infrastructure",
    "Real-time", "High-availability", "Scalable", "Distributed",
    "Machine Learning", "AI", "Deep Learning", "NLP", "Computer Vision",
    "Data Pipeline", "ETL", "Data Warehouse", "Analytics",
    "Mobile", "iOS", "Android", "Cross-platform",
    "Security", "Compliance", "GDPR", "SOC2", "HIPAA",
    "DevOps", "SRE", "Observability", "Monitoring",
]


class JDAnalyzerService:
    """Analyzes job descriptions and extracts structured requirements."""

    def extract_skills_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract technical skills, behavioral skills, and domain terms."""
        found_tech = []
        found_behavioral = []
        found_domain = []

        for skill in TECH_SKILLS:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text, re.IGNORECASE):
                if skill not in found_tech:
                    found_tech.append(skill)

        for skill in BEHAVIORAL_SKILLS:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text, re.IGNORECASE):
                if skill not in found_behavioral:
                    found_behavioral.append(skill)

        for term in DOMAIN_TERMS:
            pattern = r"\b" + re.escape(term) + r"\b"
            if re.search(pattern, text, re.IGNORECASE):
                if term not in found_domain:
                    found_domain.append(term)

        return {
            "technical": found_tech,
            "behavioral": found_behavioral,
            "domain": found_domain,
        }

    def classify_requirement(self, line: str) -> RequirementTypeEnum:
        """Classify a requirement line by type."""
        for pattern in EDUCATION_PATTERNS:
            if re.search(pattern, line):
                return RequirementTypeEnum.EDUCATION

        for pattern in EXPERIENCE_PATTERNS:
            if re.search(pattern, line):
                return RequirementTypeEnum.EXPERIENCE

        for pattern in RESPONSIBILITY_INDICATORS:
            if re.search(pattern, line):
                return RequirementTypeEnum.RESPONSIBILITY

        for pattern in PREFERRED_INDICATORS:
            if re.search(pattern, line):
                return RequirementTypeEnum.PREFERRED

        for pattern in BEHAVIORAL_SKILLS:
            if re.search(r"\b" + re.escape(pattern) + r"\b", line, re.IGNORECASE):
                return RequirementTypeEnum.BEHAVIORAL

        return RequirementTypeEnum.REQUIRED

    def determine_importance(self, line: str, section_context: str = "") -> str:
        """Determine if a requirement is required or preferred."""
        combined = f"{section_context} {line}".lower()
        for pattern in PREFERRED_INDICATORS:
            if re.search(pattern, combined):
                return "preferred"
        return "required"

    def detect_sections(self, text: str) -> Dict[str, str]:
        """Detect JD sections like responsibilities, qualifications, etc."""
        sections = {}
        current_section = "general"
        sections[current_section] = []

        jd_section_patterns = {
            "responsibilities": [
                r"(?i)^(key\s+)?responsibilities",
                r"(?i)^what\s+you.?ll?\s+do",
                r"(?i)^the\s+role",
                r"(?i)^your\s+role",
                r"(?i)^job\s+duties",
            ],
            "qualifications": [
                r"(?i)^(required\s+)?qualifications",
                r"(?i)^requirements?$",
                r"(?i)^what\s+you.?ll?\s+(?:need|bring)",
                r"(?i)^what\s+we.?re?\s+looking\s+for",
                r"(?i)^who\s+you\s+are",
                r"(?i)^you\s+have",
                r"(?i)^must\s+have",
            ],
            "preferred": [
                r"(?i)^preferred\s+qualifications",
                r"(?i)^nice\s+to\s+have",
                r"(?i)^bonus\s+(?:points|qualifications)",
            ],
            "about": [
                r"(?i)^about\s+(?:us|the\s+(?:company|team|role))",
                r"(?i)^who\s+we\s+are",
                r"(?i)^company\s+(?:overview|description)",
            ],
            "benefits": [
                r"(?i)^(?:benefits?|perks?|what\s+we\s+offer)",
                r"(?i)^compensation",
            ],
        }

        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue

            matched_section = None
            for section_name, patterns in jd_section_patterns.items():
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

    def extract_experience_requirements(self, text: str) -> List[str]:
        """Extract experience-related requirements."""
        results = []
        for pattern in EXPERIENCE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get the full line containing the match
                start = text.rfind("\n", 0, match.start()) + 1
                end = text.find("\n", match.end())
                if end == -1:
                    end = len(text)
                line = text[start:end].strip()
                line = re.sub(r"^[•\-–▪○●◆*]\s*", "", line)
                if line and line not in results:
                    results.append(line)
        return results

    def extract_education_requirements(self, text: str) -> List[str]:
        """Extract education-related requirements."""
        results = []
        for pattern in EDUCATION_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start = text.rfind("\n", 0, match.start()) + 1
                end = text.find("\n", match.end())
                if end == -1:
                    end = len(text)
                line = text[start:end].strip()
                line = re.sub(r"^[•\-–▪○●◆*]\s*", "", line)
                if line and line not in results:
                    results.append(line)
        return results

    def extract_responsibilities(self, text: str) -> List[str]:
        """Extract responsibility bullet points."""
        results = []
        for line in text.split("\n"):
            stripped = line.strip()
            stripped = re.sub(r"^[•\-–▪○●◆*]\s*", "", stripped)
            if not stripped:
                continue
            for pattern in RESPONSIBILITY_INDICATORS:
                if re.search(pattern, stripped):
                    if stripped not in results:
                        results.append(stripped)
                    break
        return results

    async def analyze(self, raw_text: str, title: str = "", company: str = "") -> ParsedJobDescription:
        """Full JD analysis pipeline."""
        # Extract skills
        skills_data = self.extract_skills_from_text(raw_text)

        # Detect sections
        sections = self.detect_sections(raw_text)

        # Separate required vs preferred skills based on context
        required_skills = []
        preferred_skills = []

        qual_text = sections.get("qualifications", "")
        pref_text = sections.get("preferred", "")

        # Skills in qualifications → required
        qual_skills = self.extract_skills_from_text(qual_text)
        required_skills = qual_skills.get("technical", [])

        # Skills in preferred section → preferred
        pref_skills = self.extract_skills_from_text(pref_text)
        preferred_skills = pref_skills.get("technical", [])

        # Skills found but not in either section → default to required
        for skill in skills_data["technical"]:
            if skill not in required_skills and skill not in preferred_skills:
                required_skills.append(skill)

        # Extract structured requirements
        experience_reqs = self.extract_experience_requirements(raw_text)
        education_reqs = self.extract_education_requirements(raw_text)
        responsibilities = self.extract_responsibilities(
            sections.get("responsibilities", raw_text)
        )

        # Build requirement entries with classification
        requirements = []
        for line in raw_text.split("\n"):
            stripped = line.strip()
            stripped = re.sub(r"^[•\-–▪○●◆*\d.)\]]\s*", "", stripped)
            if len(stripped) > 15:  # Skip very short lines
                req_type = self.classify_requirement(stripped)
                importance = self.determine_importance(stripped)
                requirements.append(RequirementEntry(
                    text=stripped,
                    type=req_type,
                    importance=importance,
                ))

        # Extract title from text if not provided
        if not title:
            lines = raw_text.strip().split("\n")
            if lines:
                title = lines[0].strip()

        return ParsedJobDescription(
            title=title,
            company=company,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            experience_requirements=experience_reqs,
            education_requirements=education_reqs,
            responsibilities=responsibilities,
            domain_terms=skills_data["domain"],
            behavioral_requirements=skills_data["behavioral"],
            requirements=requirements,
        )


# Singleton
jd_analyzer = JDAnalyzerService()

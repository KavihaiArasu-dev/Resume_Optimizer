"""
Skill Ontology & Normalization — Blueprint Section 9.
Recognizes equivalent terminology and related technologies.
"""
from typing import Dict, List, Set, Optional, Tuple


# ─── Skill Aliases (equivalent terminology) ────────────────────────────────

SKILL_ALIASES: Dict[str, List[str]] = {
    # Languages
    "javascript": ["js", "ecmascript", "es6", "es6+", "es2015", "es2020", "es2021"],
    "typescript": ["ts"],
    "python": ["py", "python3", "python 3"],
    "c++": ["cpp", "c plus plus"],
    "c#": ["csharp", "c sharp"],
    "golang": ["go"],

    # Frontend
    "react": ["react.js", "reactjs", "react js"],
    "react native": ["react-native", "rn"],
    "angular": ["angularjs", "angular.js", "angular 2+"],
    "vue": ["vue.js", "vuejs", "vue js", "vue 3"],
    "next.js": ["nextjs", "next js", "next"],
    "nuxt.js": ["nuxtjs", "nuxt js", "nuxt"],
    "tailwind css": ["tailwind", "tailwindcss"],
    "material ui": ["mui", "material-ui", "material design"],

    # Backend
    "node.js": ["nodejs", "node js", "node"],
    "express": ["express.js", "expressjs"],
    "fastapi": ["fast api", "fast-api"],
    "django": ["django rest framework", "drf"],
    "spring": ["spring boot", "springboot"],
    "ruby on rails": ["rails", "ror"],
    "asp.net": ["asp.net core", ".net", "dotnet"],

    # Databases
    "postgresql": ["postgres", "psql", "pg"],
    "mongodb": ["mongo"],
    "mysql": ["my sql"],
    "elasticsearch": ["elastic", "es"],
    "dynamodb": ["dynamo db", "dynamo"],
    "sql server": ["mssql", "microsoft sql server"],

    # Cloud & DevOps
    "aws": ["amazon web services", "aws cloud"],
    "lambda": ["aws lambda", "aws-lambda"],
    "gcp": ["google cloud", "google cloud platform"],
    "azure": ["microsoft azure"],
    "kubernetes": ["k8s", "kube"],
    "docker": ["docker container", "containerization"],
    "terraform": ["tf", "hcl"],
    "ci/cd": ["ci cd", "continuous integration", "continuous deployment", "continuous delivery"],
    "github actions": ["gh actions"],


    # Data & AI
    "machine learning": ["ml", "machine-learning"],
    "deep learning": ["dl", "deep-learning"],
    "natural language processing": ["nlp"],
    "computer vision": ["cv"],
    "tensorflow": ["tf"],
    "pytorch": ["torch"],
    "scikit-learn": ["sklearn", "scikit learn"],
    "pandas": ["pd"],
    "numpy": ["np"],

    # Tools
    "visual studio code": ["vscode", "vs code"],
    "intellij": ["intellij idea"],
    "postman": ["postman api"],
    "git": ["version control"],

    # Concepts
    "rest api": ["restful", "restful api", "rest apis", "restful apis", "rest"],
    "graphql": ["gql"],
    "microservices": ["micro services", "micro-services"],
    "serverless": ["server-less", "faas", "function as a service"],
    "agile": ["agile methodology", "agile development"],
    "scrum": ["scrum methodology"],
    "devops": ["dev ops", "dev-ops"],
    "oauth": ["oauth2", "oauth 2.0"],
    "jwt": ["json web token", "json web tokens"],
}

# ─── Technology Relationships (parent/child, related) ──────────────────────

TECH_RELATIONSHIPS: Dict[str, Dict[str, List[str]]] = {
    "aws": {
        "children": [
            "lambda", "ec2", "s3", "dynamodb", "rds", "ecs", "eks",
            "api gateway", "cloudwatch", "cloudformation", "sqs", "sns",
            "cognito", "iam", "route 53", "cloudfront", "sagemaker",
            "step functions", "eventbridge",
        ],
        "related": ["cloud", "serverless", "infrastructure"],
    },
    "gcp": {
        "children": [
            "cloud functions", "cloud run", "bigquery", "cloud storage",
            "gke", "firebase", "pub/sub", "cloud sql", "vertex ai",
        ],
        "related": ["cloud", "serverless", "infrastructure"],
    },
    "azure": {
        "children": [
            "azure functions", "azure devops", "cosmos db", "azure sql",
            "aks", "app service", "blob storage", "logic apps",
        ],
        "related": ["cloud", "serverless", "infrastructure"],
    },
    "react": {
        "children": ["jsx", "hooks", "redux", "context api", "react router"],
        "related": ["frontend", "spa", "ui", "javascript", "typescript"],
    },
    "node.js": {
        "children": ["express", "nestjs", "koa", "hapi", "fastify"],
        "related": ["backend", "javascript", "server-side"],
    },
    "python": {
        "children": ["django", "flask", "fastapi", "celery", "sqlalchemy"],
        "related": ["backend", "data science", "machine learning", "scripting"],
    },
    "docker": {
        "children": ["dockerfile", "docker-compose", "docker hub"],
        "related": ["containerization", "kubernetes", "devops"],
    },
    "kubernetes": {
        "children": ["helm", "kubectl", "pod", "deployment", "service", "ingress"],
        "related": ["container orchestration", "docker", "devops"],
    },
    "postgresql": {
        "children": ["pgvector", "plpgsql", "pg_dump"],
        "related": ["sql", "database", "rdbms", "relational database"],
    },
    "mongodb": {
        "children": ["mongoose", "mongosh", "atlas"],
        "related": ["nosql", "database", "document database"],
    },
    "machine learning": {
        "children": [
            "supervised learning", "unsupervised learning", "reinforcement learning",
            "classification", "regression", "clustering",
        ],
        "related": ["ai", "data science", "deep learning", "nlp"],
    },
}


class SkillOntology:
    """Handles skill normalization, alias resolution, and relationship mapping."""

    def __init__(self):
        # Build reverse alias lookup: alias → canonical name
        self._alias_map: Dict[str, str] = {}
        for canonical, aliases in SKILL_ALIASES.items():
            self._alias_map[canonical.lower()] = canonical
            for alias in aliases:
                self._alias_map[alias.lower()] = canonical

        # Build child-to-parent lookup
        self._child_to_parent: Dict[str, str] = {}
        for parent, rels in TECH_RELATIONSHIPS.items():
            for child in rels.get("children", []):
                self._child_to_parent[child.lower()] = parent

    def normalize(self, skill: str) -> str:
        """Normalize a skill name to its canonical form."""
        key = skill.lower().strip()
        return self._alias_map.get(key, skill)

    def normalize_list(self, skills: List[str]) -> List[str]:
        """Normalize a list of skills, deduplicating."""
        seen = set()
        result = []
        for skill in skills:
            normalized = self.normalize(skill)
            key = normalized.lower()
            if key not in seen:
                seen.add(key)
                result.append(normalized)
        return result

    def are_equivalent(self, skill_a: str, skill_b: str) -> bool:
        """Check if two skill names refer to the same technology."""
        return self.normalize(skill_a).lower() == self.normalize(skill_b).lower()

    def are_related(self, skill_a: str, skill_b: str) -> Tuple[bool, str]:
        """
        Check if two skills are related (parent/child or related concepts).
        Returns (is_related, relationship_type).
        """
        norm_a = self.normalize(skill_a).lower()
        norm_b = self.normalize(skill_b).lower()

        # Direct equivalence
        if norm_a == norm_b:
            return True, "exact"

        # Check if one is a child of the other
        if norm_a in TECH_RELATIONSHIPS:
            children = [c.lower() for c in TECH_RELATIONSHIPS[norm_a].get("children", [])]
            if norm_b in children:
                return True, "child"
            related = [r.lower() for r in TECH_RELATIONSHIPS[norm_a].get("related", [])]
            if norm_b in related:
                return True, "related"

        if norm_b in TECH_RELATIONSHIPS:
            children = [c.lower() for c in TECH_RELATIONSHIPS[norm_b].get("children", [])]
            if norm_a in children:
                return True, "parent"
            related = [r.lower() for r in TECH_RELATIONSHIPS[norm_b].get("related", [])]
            if norm_a in related:
                return True, "related"

        # Check shared parent
        parent_a = self._child_to_parent.get(norm_a)
        parent_b = self._child_to_parent.get(norm_b)
        if parent_a and parent_b and parent_a == parent_b:
            return True, "sibling"

        return False, ""

    def get_children(self, skill: str) -> List[str]:
        """Get child technologies of a skill."""
        norm = self.normalize(skill).lower()
        if norm in TECH_RELATIONSHIPS:
            return TECH_RELATIONSHIPS[norm].get("children", [])
        return []

    def get_related(self, skill: str) -> List[str]:
        """Get related technologies."""
        norm = self.normalize(skill).lower()
        if norm in TECH_RELATIONSHIPS:
            return TECH_RELATIONSHIPS[norm].get("related", [])
        return []

    def get_parent(self, skill: str) -> Optional[str]:
        """Get parent technology if this skill is a child."""
        key = skill.lower().strip()
        return self._child_to_parent.get(key)

    def find_all_matches(self, skill: str, candidate_skills: List[str]) -> List[Dict]:
        """
        Find all ways a required skill matches against candidate skills.
        Returns list of {skill, match_type, confidence}.
        """
        matches = []
        norm_required = self.normalize(skill)

        for candidate_skill in candidate_skills:
            norm_candidate = self.normalize(candidate_skill)

            # Exact normalized match
            if norm_required.lower() == norm_candidate.lower():
                matches.append({
                    "skill": candidate_skill,
                    "match_type": "exact",
                    "confidence": 1.0,
                })
                continue

            # Relationship match
            is_related, rel_type = self.are_related(skill, candidate_skill)
            if is_related:
                confidence_map = {
                    "child": 0.85,
                    "parent": 0.70,
                    "related": 0.50,
                    "sibling": 0.60,
                }
                matches.append({
                    "skill": candidate_skill,
                    "match_type": f"ontology_{rel_type}",
                    "confidence": confidence_map.get(rel_type, 0.5),
                })

        return matches


# Singleton
skill_ontology = SkillOntology()

"""
Sample Data Set — 5 Diverse Real-World Resumes and Target Job Descriptions:
1. Full Stack Developer (React / Node / PostgreSQL / Cloud)
2. Data Analyst (SQL / Python / Tableau / PowerBI / Statistics)
3. AI/ML Engineer (PyTorch / LLMs / NLP / Vector DBs / MLOps)
4. Cloud & DevOps Engineer (AWS / Kubernetes / Terraform / CI/CD / Docker)
5. Technical Product Manager (Agile / Roadmap / User Stories / Analytics / APIs)
"""

SAMPLE_PAIRS = [
    {
        "role": "Full Stack Developer",
        "company": "Stripe",
        "resume": """Alex Morgan
alex.morgan@email.com • (555) 234-5678 • San Francisco, CA • linkedin.com/in/alexmorgan • github.com/alexmorgan

PROFESSIONAL SUMMARY
Full Stack Software Engineer with 5+ years of experience designing scalable distributed web platforms, resilient APIs, and modern frontend interfaces using TypeScript, React, Node.js, and PostgreSQL.

TECHNICAL SKILLS
Languages: TypeScript, JavaScript, Python, SQL, HTML5, CSS3
Frontend: React, Redux Toolkit, Next.js, Tailwind CSS, Webpack
Backend: Node.js, Express, FastAPI, REST APIs, GraphQL
Databases: PostgreSQL, Redis, MongoDB
Cloud & DevOps: AWS (S3, EC2, Lambda), Docker, Git, GitHub Actions, CI/CD

WORK EXPERIENCE
Senior Full Stack Engineer | FinTech Systems Inc.
Jan 2022 - Present | San Francisco, CA
• Architected payment processing microservices handling 250,000 daily transactions with 99.99% uptime.
• Developed responsive user checkout interfaces in React and TypeScript, decreasing checkout abandonment by 18%.
• Optimized PostgreSQL query performance and configured Redis caching, reducing API latency from 450ms to 85ms.
• Built automated CI/CD deployment pipelines using Docker and GitHub Actions, cutting release cycle time by 40%.

Software Engineer | CloudScale Solutions
Jun 2019 - Dec 2021 | San Jose, CA
• Designed and maintained multi-tenant RESTful APIs using Node.js, Express, and PostgreSQL serving 1.2M monthly active users.
• Created real-time analytics dashboards in React with dynamic chart rendering.
• Integrated AWS S3 and Lambda for automated PDF report generation and async document storage.

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley • 2015 - 2019 • GPA: 3.8

PROJECTS
OpenPay Core: Open-source developer SDK for asynchronous payment reconciliation built with Node.js and TypeScript.
""",
        "jd": """Senior Full Stack Engineer (Payments)
Stripe • San Francisco, CA

About the Role:
We are looking for a Senior Full Stack Engineer to lead our payments and billing infrastructure. You will architect high-throughput services and build intuitive developer-facing dashboards.

Key Responsibilities:
• Build resilient, low-latency APIs and distributed systems handling millions of financial transactions.
• Develop performant web applications using React and TypeScript.
• Own end-to-end architecture from PostgreSQL schema design to cloud deployment on AWS.
• Partner with product managers and security engineers to uphold PCI-DSS standards and idempotency.

Requirements (Required):
• 4+ years of professional full-stack software development experience.
• Strong proficiency in TypeScript, React, and Node.js.
• Deep experience with relational databases, specifically PostgreSQL.
• Experience designing and scaling RESTful APIs and microservices.
• Hands-on familiarity with cloud platforms, especially AWS (Lambda, ECS, S3) and Docker.

Preferred Qualifications:
• Experience with Redis caching and Kafka streaming.
• Understanding of payment idempotency, webhook delivery, and distributed transactions.
• Degree in Computer Science or equivalent practical experience.
"""
    },
    {
        "role": "Data Analyst",
        "company": "Spotify",
        "resume": """Jordan Lee
jordan.lee@analytics.com • (555) 345-6789 • New York, NY • linkedin.com/in/jordanlee

PROFESSIONAL SUMMARY
Data Analyst with 4 years of experience translating complex datasets into actionable business intelligence. Specialized in SQL query optimization, Python data modeling, and executive dashboard development in Tableau and Power BI.

TECHNICAL SKILLS
Languages: SQL, Python, R
Tools & Visualization: Tableau, Power BI, Excel, dbt, Snowflake, BigQuery
Libraries: Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn
Methodologies: A/B Testing, Cohort Analysis, Hypothesis Testing, ETL Pipelines

WORK EXPERIENCE
Lead Business Data Analyst | MediaPulse Corp
Feb 2022 - Present | New York, NY
• Built automated executive dashboards in Tableau tracking customer churn across 4M subscribers, saving 15 manual reporting hours weekly.
• Formulated complex SQL data pipelines in Snowflake and dbt to measure user retention and engagement KPIs.
• Designed and analyzed 25+ statistical A/B tests on content recommendation carousels, driving a 7.5% lift in average stream duration.
• Collaborated with product leaders to identify drop-off points in user onboarding funnels.

Junior Data Analyst | InsightRetail Inc.
Aug 2020 - Jan 2022 | Boston, MA
• Queried relational PostgreSQL databases to audit inventory turnover and forecast quarterly vendor demand.
• Built Python ETL scripts using Pandas to clean and merge disparate customer telemetry logs.
• Produced weekly executive KPI decks in Power BI with actionable growth recommendations.

EDUCATION
Bachelor of Science in Statistics and Data Science
New York University • 2016 - 2020 • GPA: 3.7
""",
        "jd": """Product Data Analyst (Music Discovery)
Spotify • New York, NY

Responsibilities:
• Analyze behavioral data from millions of listeners to uncover discovery trends and improve playlist personalization.
• Define core product metrics, build self-serve Tableau dashboards, and deliver data narratives to product managers.
• Design, execute, and analyze rigorous A/B experiments to evaluate algorithmic recommendations.
• Write high-efficiency SQL queries and data transformation models in Snowflake or BigQuery.

Required Qualifications:
• 3+ years of data analysis experience supporting consumer-facing digital products.
• Advanced SQL skills (window functions, query plan optimization, complex joins).
• Proficiency in Python (Pandas, NumPy) for exploratory data analysis.
• Proven track record creating interactive dashboards in Tableau or Power BI.
• Deep grounding in experimental design, A/B testing, and statistical significance.

Preferred Qualifications:
• Experience with dbt or modern data stack tooling.
• Background in streaming, media, or subscription-based business models.
"""
    },
    {
        "role": "AI/ML Engineer",
        "company": "Anthropic",
        "resume": """Dr. Elena Rostova
elena.rostova@ai-research.org • (555) 789-0123 • Seattle, WA • linkedin.com/in/elenarostova • github.com/erostova

PROFESSIONAL SUMMARY
AI/ML Engineer with expertise in Large Language Models (LLMs), natural language processing, vector retrieval, and production deep learning pipelines using PyTorch, Hugging Face, LangChain, and Qdrant.

TECHNICAL SKILLS
Languages: Python, C++, Bash
Frameworks & Libraries: PyTorch, TensorFlow, Hugging Face Transformers, LangChain, LlamaIndex, vLLM
Data & Vectors: PostgreSQL (pgvector), Qdrant, Pinecone, FAISS, Pandas, NumPy
Cloud & MLOps: AWS SageMaker, Docker, Kubernetes, Triton Inference Server, MLflow

WORK EXPERIENCE
Senior Machine Learning Engineer | Cognition Labs
Mar 2022 - Present | Seattle, WA
• Engineered a Retrieval-Augmented Generation (RAG) system serving enterprise search over 10M documents with <120ms retrieval latency.
• Fine-tuned 7B/13B parameter open-source transformer models using LoRA and QLoRA for domain-specific contract analysis.
• Optimized model inference using vLLM and TensorRT-LLM, cutting GPU memory overhead by 45% and doubling token throughput.
• Deployed high-throughput Triton inference clusters on Kubernetes orchestrated with AWS EKS.

Machine Learning Researcher | Apex AI Institute
Sep 2020 - Feb 2022 | San Francisco, CA
• Developed novel semantic embedding models using PyTorch for multilingual classification tasks.
• Evaluated hallucination mitigation mechanisms and factual consistency validation in text generation models.

EDUCATION
Ph.D. in Computer Science (Specialization in Natural Language Processing)
University of Washington • 2016 - 2020
Bachelor of Science in Mathematics and Computer Science
University of Washington • 2012 - 2016
""",
        "jd": """Machine Learning Engineer (Applied AI / Inference)
Anthropic • Seattle, WA or Remote

About the Role:
We are looking for an ML Engineer to build scalable evaluation and inference infrastructure for state-of-the-art language models.

Key Responsibilities:
• Design and optimize low-latency LLM serving and retrieval infrastructure.
• Build automated evaluation frameworks to measure model alignment, factual accuracy, and safety.
• Work with tokenizers, attention mechanisms, and model compression techniques (quantization, distillation).
• Scale vector indexing and semantic retrieval pipelines over enterprise knowledge bases.

Required Qualifications:
• 3+ years of hands-on ML engineering experience in NLP or deep learning.
• Mastery of Python and PyTorch.
• Experience with Transformer architectures, Hugging Face, and inference engines (vLLM, TensorRT-LLM, or Triton).
• Experience with vector databases (Qdrant, Pinecone, FAISS, or pgvector).
• Strong understanding of Docker, Kubernetes, and cloud compute environments.

Preferred Qualifications:
• Contributions to open-source LLM tooling or published research in NLP.
• Familiarity with fine-tuning techniques (LoRA, PEFT) and synthetic data curation.
"""
    },
    {
        "role": "DevOps & Cloud Engineer",
        "company": "HashiCorp",
        "resume": """Marcus Vance
marcus.vance@infra.dev • (555) 456-7890 • Austin, TX • linkedin.com/in/marcusvance • github.com/mvance-ops

PROFESSIONAL SUMMARY
DevOps & Cloud Infrastructure Engineer with 6 years of experience automating multi-cloud environments, Kubernetes orchestration, and Infrastructure-as-Code (Terraform) to ensure high reliability and zero-downtime deployments.

TECHNICAL SKILLS
Cloud: AWS (IAM, VPC, EKS, RDS, S3, Route53), GCP, Azure
IaC & Config: Terraform, Terragrunt, Ansible, CloudFormation
Containers & Orchestration: Kubernetes, Docker, Helm, ArgoCD, Istio
CI/CD: GitHub Actions, GitLab CI, Jenkins
Monitoring & Observability: Prometheus, Grafana, Datadog, ELK Stack, OpenTelemetry

WORK EXPERIENCE
Senior DevOps Engineer | CloudNative Systems
Jan 2021 - Present | Austin, TX
• Designed modular Terraform codebases managing 14 production AWS accounts across 3 regions with zero configuration drift.
• Migrated 60+ legacy containerized services to Amazon EKS with ArgoCD GitOps, improving deployment frequency from weekly to 12+ daily.
• Configured Prometheus, Grafana, and Datadog monitoring with automated alerting, reducing MTTR by 35%.
• Enforced security compliance and least-privilege IAM policies, achieving SOC2 Type II certification.

Site Reliability Engineer | ScaleFast Inc.
Jul 2018 - Dec 2020 | Dallas, TX
• Maintained Kubernetes clusters handling 40,000 requests/sec with 99.95% service level availability.
• Built end-to-end CI/CD pipelines in GitLab CI and Docker for automated unit testing and container image scanning.
• Automated database backup snapshots and disaster recovery drill procedures for PostgreSQL on AWS RDS.

EDUCATION
Bachelor of Science in Information Technology
University of Texas at Austin • 2014 - 2018
""",
        "jd": """Senior Cloud Infrastructure / DevOps Engineer
HashiCorp • Austin, TX or Remote

What You Will Do:
• Architect, provision, and maintain resilient cloud infrastructure using Terraform and Kubernetes.
• Build developer tooling, self-service CI/CD deployment pipelines, and zero-trust networking systems.
• Champion observability, automated chaos testing, and disaster recovery drills.

Required Skills:
• 5+ years of experience in DevOps, Cloud Engineering, or SRE roles.
• Production expertise with Infrastructure as Code using Terraform.
• Deep expertise running production Kubernetes (EKS, GKE, or self-hosted) and Helm.
• Strong experience with AWS cloud networking (VPC, Transit Gateway, Route53, IAM).
• Experience building CI/CD automation with GitHub Actions or GitLab CI.

Preferred Skills:
• Experience with GitOps methodologies (ArgoCD or Flux).
• Hands-on proficiency with Prometheus, Grafana, and OpenTelemetry distributed tracing.
• Python or Go scripting proficiency.
"""
    },
    {
        "role": "Technical Product Manager",
        "company": "Atlassian",
        "resume": """Samantha Reed
samantha.reed@pmgrowth.com • (555) 890-1234 • Chicago, IL • linkedin.com/in/samanthareed

PROFESSIONAL SUMMARY
Technical Product Manager with 5+ years of experience leading cross-functional engineering and design teams to deliver high-adoption SaaS products, developer APIs, and workflow automation tools.

SKILLS & COMPETENCIES
Product Management: Product Roadmapping, PRDs, User Story Mapping, Backlog Grooming, Wireframing
Technical Acumen: REST APIs, SQL, Agile/Scrum, JIRA, Confluence, System Architecture Fundamentals
Analytics & Metrics: Mixpanel, Google Analytics, Amplitude, A/B Testing, Retention Modeling, OKRs

WORK EXPERIENCE
Senior Technical Product Manager | CollabFlow Inc.
May 2021 - Present | Chicago, IL
• Led product strategy and execution for a developer API platform adopted by 150+ enterprise integrations.
• Authored comprehensive PRDs and user stories for workflow automation features that drove a 24% increase in user retention.
• Spearheaded quarterly roadmap planning aligning engineering, design, marketing, and sales leadership.
• Established quantitative product telemetry in Amplitude tracking funnel drop-off, guiding data-driven sprint priorities.

Product Manager | TeamSync Software
Sep 2018 - Apr 2021 | Chicago, IL
• Managed backlog and sprint ceremonies for two Scrum teams (14 engineers, 2 designers) delivering SaaS productivity tooling.
• Conducted 50+ user interviews to identify usability friction and define technical requirements for mobile app redesign.
• Increased monthly active user engagement by 19% through iterative feature releases and customer onboarding improvements.

EDUCATION
Bachelor of Arts in Economics & Minor in Computer Science
Northwestern University • 2014 - 2018
Certifications: Certified Scrum Product Owner (CSPO)
""",
        "jd": """Senior Technical Product Manager (Developer Platform)
Atlassian • Remote / Chicago, IL

About the Role:
We are seeking a Senior Technical Product Manager to define the vision and technical roadmap for our ecosystem platform and third-party developer APIs.

Responsibilities:
• Define product strategy, maintain prioritization backlogs, and write crisp PRDs and API technical specifications.
• Collaborate closely with engineering leads and systems architects to deliver performant and reliable platform services.
• Engage with developer communities and enterprise customers to uncover workflows, synthesize feedback, and drive adoption.
• Define and measure product success metrics, retention curves, and adoption KPIs.

Required Qualifications:
• 4+ years of product management experience managing technical, platform, or API products.
• Demonstrated ability to write detailed technical requirements, API specs, and user stories.
• Strong analytical mindset with experience querying SQL and analyzing user engagement metrics.
• Proven track record leading Agile/Scrum cross-functional engineering teams.

Preferred Qualifications:
• Prior background in software engineering, technical consulting, or computer science degree.
• CSPO or Pragmatic Institute certifications.
"""
    }
]

import type { PresetScenario, OptimizationResult } from '../types';

export const PRESET_SCENARIOS: PresetScenario[] = [
  {
    id: 'stripe-fullstack',
    label: 'Senior Full-Stack Engineer',
    role: 'Staff / Senior Full-Stack Engineer',
    company: 'Stripe',
    resumeFileName: 'Alex_Chen_Staff_Engineer_Resume.pdf',
    resumeText: `ALEX CHEN
San Francisco, CA | alex.chen@example.com | +1 (555) 234-5678 | linkedin.com/in/alexchen-dev | github.com/alexchen

SUMMARY
Senior Software Engineer with 6+ years of experience designing high-throughput distributed systems, payments infrastructure, and modern React web applications. Proven track record leading multi-service architectures and scaling latency-critical systems.

EXPERIENCE
Lead Full-Stack Engineer | FinCore Technologies
Jun 2021 – Present | San Francisco, CA
- Worked on payments processing pipeline handling credit card transactions and settlements.
- Migrated monolith service to microservices written in TypeScript and Go.
- Built customer-facing dashboard in React and Redux with GraphQL queries.
- Improved database query performance on PostgreSQL cluster.
- Mentored 4 junior engineers and led bi-weekly technical design reviews.

Software Engineer | HyperScale Cloud Labs
Feb 2018 – May 2021 | Seattle, WA
- Developed REST APIs and background workers in Python and FastAPI.
- Implemented real-time telemetry streaming pipeline with Apache Kafka and Redis.
- Configured CI/CD deployment pipelines on AWS using Terraform and Docker.
- Reduced build times for frontend assets.

EDUCATION
B.S. in Computer Science | University of California, Berkeley (2014 – 2018)

SKILLS
Languages: TypeScript, JavaScript, Python, Go, SQL
Frontend: React, Next.js, Redux, Tailwind CSS, HTML5, WebSockets
Backend: Node.js, Express, FastAPI, GraphQL, gRPC
Infrastructure & Storage: PostgreSQL, Redis, Kafka, Docker, Kubernetes, AWS, Terraform`,
    jobDescriptionText: `Senior / Staff Full-Stack Engineer — Payments Infrastructure
Stripe — Financial Systems Org
San Francisco, CA (Hybrid / Remote)

About the Role:
We are seeking an experienced Senior Full-Stack Engineer to architect and build our next-generation payment ledger and real-time merchant transaction visualization platform. You will be responsible for end-to-end design, high-availability distributed systems, idempotent payment processing, and mission-critical merchant interfaces.

Key Responsibilities:
- Design fault-tolerant payment processing pipelines capable of processing 10,000+ financial transactions per second with 99.999% availability.
- Build high-performance, accessible merchant dashboard experiences using React, TypeScript, and modern state architectures.
- Implement strictly idempotent REST/gRPC interfaces and event-driven data streaming via Apache Kafka and distributed ledgers.
- Drive database schema design, index optimization, and horizontal partitioning for PostgreSQL and Redis caches.
- Champion rigorous testing, automated canary deployments, telemetry tracing with OpenTelemetry, and zero-downtime database migrations.

Required Qualifications:
- 5+ years of full-stack or backend systems engineering experience with TypeScript/JavaScript and Python or Go.
- Proven experience with distributed systems, transaction processing, and data consistency models (ACID, event sourcing, idempotency keys).
- Deep proficiency with modern React, TypeScript, and robust client-side state management.
- Hands-on expertise with PostgreSQL query performance tuning, index strategies, and Redis distributed caching.
- Experience with message queues (Kafka, RabbitMQ) and microservice orchestration (Docker, Kubernetes).

Preferred Qualifications:
- Experience in fintech, PCI-DSS compliance, or automated reconciliation engines.
- Familiarity with Infrastructure as Code (Terraform) and AWS/GCP cloud environments.
- Active contribution to open-source software or engineering blogs.`,
  },
  {
    id: 'openai-ml',
    label: 'AI / ML Platform Engineer',
    role: 'Senior Machine Learning Systems Engineer',
    company: 'OpenAI / Anthropic',
    resumeFileName: 'Elena_Rostova_ML_Systems_Resume.docx',
    resumeText: `ELENA ROSTOVA
Seattle, WA | elena.rostova@example.com | +1 (555) 987-6543 | github.com/erostova-ml

SUMMARY
Machine Learning Systems Engineer with 5 years of experience deploying LLM inference pipelines, vector search infrastructure, and distributed GPU training clusters.

EXPERIENCE
Senior ML Engineer | Cognition Labs
2022 – Present | Seattle, WA
- Deployed transformer models using vLLM and TensorRT-LLM on NVIDIA H100 clusters.
- Built hybrid retrieval augmented generation (RAG) system with Qdrant vector database and LangChain.
- Optimized model quantization from FP16 to INT4 reducing memory consumption by 62%.
- Created automated evaluation framework benchmarking hallucination rates across 50,000 test prompts.

Machine Learning Engineer | Apex Data Systems
2019 – 2022 | Austin, TX
- Trained classification models using PyTorch and Hugging Face Transformers.
- Designed feature store pipelines with Apache Spark and Redis.
- Implemented MLOps workflows with Kubeflow and MLflow.

EDUCATION
M.S. in Machine Learning & Robotics | University of Washington (2017 – 2019)
B.S. in Applied Mathematics | UT Austin (2013 – 2017)

SKILLS
ML Frameworks: PyTorch, Hugging Face, TensorRT, vLLM, ONNX, scikit-learn
AI/LLM: Vector Search (Qdrant, Pinecone), LangChain, LlamaIndex, Prompt Engineering, Quantization
Infrastructure: CUDA, Triton, Docker, Kubernetes, AWS Bedrock, GCP Vertex AI
Languages: Python, C++, SQL, Bash`,
    jobDescriptionText: `Senior Machine Learning Systems Engineer — Inference Infrastructure
OpenAI — Scaled Inference Team
San Francisco, CA / Seattle, WA

Role Overview:
Join the team scaling our generative AI models to hundreds of millions of daily queries. We are looking for an ML Systems Engineer with deep knowledge of distributed GPU kernels, LLM serving engines, and low-latency inference runtimes.

Requirements:
- Strong programming background in Python, modern C++, and CUDA kernel tuning.
- Production experience with high-throughput LLM inference frameworks (vLLM, TensorRT-LLM, Triton Inference Server).
- Understanding of KV cache management, continuous batching, and speculative decoding.
- Experience with vector similarity engines (Qdrant, Milvus) and embedding retrieval pipelines.
- Master's or Bachelor's in CS, Mathematics, or equivalent field.`,
  },
];

export const MOCK_RESULTS: Record<string, OptimizationResult> = {
  'stripe-fullstack': {
    matchId: 'match-stripe-fullstack-001',
    jobTitle: 'Senior Full-Stack Engineer — Payments Infrastructure',
    company: 'Stripe',
    readiness: {
      overallScore: 84,
      requiredSkills: 88,
      semanticSimilarity: 82,
      experienceAlignment: 90,
      responsibilities: 78,
      keywords: 80,
      education: 95,
      preferredSkills: 72,
    },
    atsScore: 94,
    layoutRisk: 'low',
    verdict: 'Suitable',
    verdictReasons: [
      'Strong technical alignment with Stripe payments infrastructure requirements.',
      'Required skill coverage is 88%, exceeding the 80% suitability threshold.',
    ],
    quality: {
      clarity: 90,
      achievementStrength: 85,
      quantificationRate: 65,
      unquantifiedBullets: [],
    },
    diffs: [
      {
        id: 'b1',
        section: 'Experience Bullet',
        before: 'Redesigned payments API backend in Node.js and PostgreSQL to handle more concurrent requests.',
        after: 'Architected distributed idempotent payment processing gateway in Node.js, TypeScript, and PostgreSQL, scaling throughput from 1,200 to 10,500 TPS while maintaining 99.995% transaction reliability.',
        why: 'Reframed with explicit throughput metric (10,500 TPS) and high-availability SLA.',
        requirement_addressed: 'Idempotent Payment Processing',
        applied: true,
      },
    ],
    missingMetricPrompts: [],
    prioritizedEnhancements: [
      {
        priority: 'Medium',
        action: 'Incorporate mentions of idempotent API design and secure audit logging into your FinCore transaction bullets.',
        requirement_addressed: 'PCI-DSS Compliance',
        category: 'Compliance & Auditing',
        expected_score_lift: '+6 pts',
      },
    ],
    versions: [
      {
        id: 'ver-1',
        version_name: 'Full Stack Developer',
        target_role: 'Senior Full-Stack Engineer',
        mode: 'evidence_based',
        created_at: '2026-10-22',
      },
    ],
    quantificationRate: {
      before: 35,
      after: 92,
    },
    skills: [
      {
        name: 'TypeScript',
        category: 'languages',
        importance: 'required',
        status: 'matched',
        confidence: 0.98,
        evidenceResumeSnippet: 'Migrated monolith service to microservices written in TypeScript and Go.',
        jobContextSnippet: '5+ years of full-stack engineering with TypeScript/JavaScript.',
      },
      {
        name: 'React',
        category: 'frameworks',
        importance: 'required',
        status: 'matched',
        confidence: 0.96,
        evidenceResumeSnippet: 'Built customer-facing dashboard in React and Redux with GraphQL queries.',
        jobContextSnippet: 'Build high-performance merchant dashboard experiences using React.',
      },
      {
        name: 'PostgreSQL',
        category: 'databases',
        importance: 'required',
        status: 'matched',
        confidence: 0.95,
        evidenceResumeSnippet: 'Improved database query performance on PostgreSQL cluster.',
        jobContextSnippet: 'Deep expertise with PostgreSQL query performance tuning and indexing.',
      },
      {
        name: 'Apache Kafka',
        category: 'tools',
        importance: 'required',
        status: 'matched',
        confidence: 0.92,
        evidenceResumeSnippet: 'Implemented real-time telemetry streaming pipeline with Apache Kafka and Redis.',
        jobContextSnippet: 'Event-driven data streaming via Apache Kafka and distributed ledgers.',
      },
      {
        name: 'Idempotency & Distributed Ledgers',
        category: 'concepts',
        importance: 'required',
        status: 'partial',
        confidence: 0.62,
        evidenceResumeSnippet: 'Worked on payments processing pipeline handling credit card transactions and settlements.',
        jobContextSnippet: 'Design idempotent payment processing and transaction ledger systems.',
      },
      {
        name: 'PCI-DSS Compliance',
        category: 'concepts',
        importance: 'preferred',
        status: 'not_detected',
        confidence: 0.15,
        jobContextSnippet: 'Experience in fintech, PCI-DSS compliance, or automated reconciliation.',
      },
      {
        name: 'OpenTelemetry / Tracing',
        category: 'tools',
        importance: 'preferred',
        status: 'not_detected',
        confidence: 0.20,
        jobContextSnippet: 'Telemetry tracing with OpenTelemetry and zero-downtime database migrations.',
      },
      {
        name: 'Docker & Kubernetes',
        category: 'cloud',
        importance: 'required',
        status: 'matched',
        confidence: 0.94,
        evidenceResumeSnippet: 'Configured CI/CD deployment pipelines on AWS using Terraform and Docker.',
        jobContextSnippet: 'Microservice orchestration using Docker, Kubernetes, and AWS.',
      },
      {
        name: 'Terraform',
        category: 'cloud',
        importance: 'preferred',
        status: 'matched',
        confidence: 0.90,
        evidenceResumeSnippet: 'Configured CI/CD deployment pipelines on AWS using Terraform and Docker.',
        jobContextSnippet: 'Familiarity with Infrastructure as Code (Terraform).',
      },
    ],
    bullets: [
      {
        id: 'b1',
        original: 'Worked on payments processing pipeline handling credit card transactions and settlements.',
        optimized: 'Architected high-throughput payments settlement pipeline using Go and Kafka, processing $42M+ in monthly card volume with 99.99% ledger accuracy and idempotent transaction handling.',
        reasoning: 'Transformed passive verb "Worked on" into active architecture verb, added financial volume metric ($42M/mo), reliability tier (99.99%), and explicitly surfaced Stripe-critical "idempotent transaction handling".',
        impactScoreBefore: 38,
        impactScoreAfter: 94,
        xyzFormula: {
          accomplished: 'Scalable payments settlement pipeline with 99.99% ledger accuracy',
          measuredBy: '$42M+ monthly transaction volume & zero reconciliation discrepancies',
          method: 'Architected in Go with idempotent Kafka event workers & ACID guarantees',
        },
        factCheckStatus: 'verified',
        applied: true,
      },
      {
        id: 'b2',
        original: 'Improved database query performance on PostgreSQL cluster.',
        optimized: 'Optimized PostgreSQL connection pooling and composite indexing across 180M rows, slashing p99 latency from 420ms to 65ms (84% reduction) under peak financial traffic.',
        reasoning: 'Replaced vague "improved query performance" with specific p99 benchmark latency drop (420ms -> 65ms), table scale (180M rows), and technical mechanism (composite indexing & connection pooling).',
        impactScoreBefore: 42,
        impactScoreAfter: 96,
        xyzFormula: {
          accomplished: 'Sub-100ms p99 query response across mission-critical financial databases',
          measuredBy: '84% latency decrease (420ms down to 65ms) over 180M indexed records',
          method: 'Engineered composite index structures and tuned pgBouncer pool parameters',
        },
        factCheckStatus: 'verified',
        applied: true,
      },
      {
        id: 'b3',
        original: 'Built customer-facing dashboard in React and Redux with GraphQL queries.',
        optimized: 'Engineered responsive merchant analytics portal in React and TypeScript, leveraging Apollo GraphQL caching to eliminate 60% of redundant API round-trips for 15,000+ daily active sellers.',
        reasoning: 'Highlighted merchant audience scale (15k DAU), exact caching gain (60% network request reduction), and emphasized TypeScript adherence.',
        impactScoreBefore: 45,
        impactScoreAfter: 91,
        xyzFormula: {
          accomplished: 'High-performance merchant transaction analytics portal',
          measuredBy: '60% reduction in round-trip queries and support for 15k+ daily active merchants',
          method: 'Developed with React, TypeScript, and normalized GraphQL client cache',
        },
        factCheckStatus: 'verified',
        applied: false,
      },
      {
        id: 'b4',
        original: 'Reduced build times for frontend assets.',
        optimized: 'Restructured Webpack/Vite asset compilation and dockerized caching layers, accelerating frontend CI/CD pipeline build cycles by 58% (from 14 mins to 5.8 mins).',
        reasoning: 'Provides exact before/after timing benchmarks (14m down to 5.8m) and clear engineering mechanism.',
        impactScoreBefore: 30,
        impactScoreAfter: 89,
        xyzFormula: {
          accomplished: '58% faster developer deployment and CI feedback loop',
          measuredBy: 'Build duration decreased from 14 minutes to 5.8 minutes',
          method: 'Implemented parallelized Vite caching layers and Docker layer reuse',
        },
        factCheckStatus: 'verified',
        applied: false,
      },
    ],
    atsDiagnostics: [
      {
        id: 'ats-1',
        title: 'Contact Information Parsing',
        status: 'pass',
        description: 'Email, phone number, location, LinkedIn, and GitHub URLs were cleanly extracted into structured candidate metadata.',
      },
      {
        id: 'ats-2',
        title: 'Section Header Standard Nomenclature',
        status: 'pass',
        description: 'Standard headers (SUMMARY, EXPERIENCE, EDUCATION, SKILLS) detected with 100% ATS parser recognition rate.',
      },
      {
        id: 'ats-3',
        title: 'Font and Multi-Column Layout Safety',
        status: 'pass',
        description: 'Single-column linear text stream detected. No floating text boxes, nested multi-tier tables, or non-standard glyphs.',
      },
      {
        id: 'ats-4',
        title: 'Chronological Date Format Consistency',
        status: 'pass',
        description: 'Consistent Month YYYY – Present date notation format throughout all career entries.',
      },
      {
        id: 'ats-5',
        title: 'Fintech & Security Domain Keyword Density',
        status: 'warning',
        description: 'Noticeable absence of compliance keywords like PCI-DSS, Idempotency, or Audit Trails required by Stripe Payments Org.',
        recommendation: 'Incorporate mentions of idempotent API design and secure audit logging into your FinCore transaction bullets.',
      },
      {
        id: 'ats-6',
        title: 'Telemetry & Observability Specificity',
        status: 'warning',
        description: 'The job requests OpenTelemetry or distributed tracing, but the resume only specifies generic "telemetry streaming".',
        recommendation: 'Mention OpenTelemetry or Prometheus tracing tools explicitly in the HyperScale experience section.',
      },
    ],
    missingKeywords: ['Idempotency', 'PCI-DSS', 'OpenTelemetry', 'ACID transactions', 'Event Sourcing', 'Reconciliation'],
    matchedKeywords: ['TypeScript', 'React', 'PostgreSQL', 'Kafka', 'Redis', 'Docker', 'AWS', 'Terraform', 'Microservices', 'GraphQL', 'CI/CD'],
    summarySuggestion: {
      currentSummary: 'Senior Software Engineer with 6+ years of experience designing high-throughput distributed systems, payments infrastructure, and modern React web applications.',
      recommendedSummary: 'Staff/Senior Full-Stack Engineer with 6+ years specializing in distributed payment systems, ACID-compliant ledger infrastructure, and high-performance React/TypeScript merchant applications. Track record scaling PostgreSQL and Kafka event streaming to 10k+ TPS while cutting p99 latency by 84%.',
      alignmentHighlights: [
        'Directly reflects Stripe payments ledger focus',
        'Cites verified 84% p99 latency reduction metric',
        'Includes essential keyword pairs: ACID ledger, Kafka event streaming, TypeScript',
      ],
    },
  },
};

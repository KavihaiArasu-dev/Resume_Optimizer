# AI-Powered Resume Optimizer

A production-grade, full-stack AI/NLP resume intelligence and tailoring platform built in accordance with the specialized pipeline blueprint:
`ResumeParser` → `JDAnalyzer` → `Matcher` → `Optimizer` → `FactValidator` → `ResumeGenerator`.

---

## Tech Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons, Recharts, Canvas Confetti
- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- **Document Parsing & Extraction**: PyMuPDF (`fitz`), `python-docx`, Tesseract OCR (`pytesseract`)
- **NLP, Ontology & Similarity**: Scikit-Learn TF-IDF, Sentence-Transformers (BGE/E5/MiniLM), Levenshtein Distance
- **Export & Rendering Engine**: ReportLab (ATS-Safe single column vector PDF), PyMuPDF 300 DPI High-Res Image Renderer (2x scale PNG/JPG), `python-docx` (Word .docx generator)
- **Asynchronous Execution**: In-memory job queue with real-time polling endpoint (`GET /api/tasks/{task_id}`)

---

## Quick Start & Running Locally

### 1. Backend Setup (FastAPI)

```bash
cd backend

# Create and activate virtual environment (optional but recommended)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Unix/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server on port 8000
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend API will be accessible at: `http://127.0.0.1:8000` (Interactive Swagger docs: `http://127.0.0.1:8000/docs`).

### 2. Frontend Setup (React + Vite)

```bash
cd frontend

# Install npm packages
npm install

# Start Vite development server
npm run dev
```

Frontend will be accessible at: `http://localhost:5173`. Requests to `/api/*` are automatically proxied to `http://127.0.0.1:8000`.

---

## How Scoring & The Resume Readiness Index Works

Unlike conventional tools that produce a single opaque ATS percentage, this platform implements a multi-dimensional, transparent **Resume Readiness Index** configured in `backend/app/config.py`:

```python
SCORING_WEIGHTS = {
    "required_skills": 0.30,       # 30% - Strict lexical & ontological match against hard criteria
    "semantic_similarity": 0.20,   # 20% - Dense vector embedding & cosine similarity
    "experience_alignment": 0.15, # 15% - Years of domain experience and seniority parity
    "responsibilities": 0.10,     # 10% - Deliverables vs expected day-to-day duties
    "keywords": 0.10,             # 10% - Domain keyword density & platform nomenclature
    "education": 0.10,            # 10% - Degree requirements and credentials
    "preferred_skills": 0.05,     #  5% - Nice-to-have competencies and bonus tools
}
```

### Layered Skill Matching Architecture
Skills are classified into three strict visibility statuses (avoiding accusatory phrasing like *"you don't know X"*):
- `Matched`: Exact or alias match with verifiable evidence in resume text.
- `Partial`: Family or ontology match (e.g. AWS Lambda mapped to Cloud Functions / Serverless).
- `Not detected in your resume`: Clear, objective indication that the competency was not found in the submitted draft.

**The 5-Layer Skill Pipeline:**
1. **Exact Match**: Direct case-insensitive token match.
2. **Normalized Aliases**: Direct alias normalization (e.g., `ReactJS` = `React.js` = `React`, `k8s` = `Kubernetes`, `AWS Lambda` = `Lambda`).
3. **Ontology Mapping**: Parent/child classification (e.g., `Lambda` → `AWS`, `PyTorch` → `Machine Learning`).
4. **Semantic Embeddings**: Cosine similarity against skill descriptions using vector representations.
5. **Evidence Verification**: Verifying the candidate actually used the technology in their project/work bullets rather than listing it in a vacuum.

### Verdict Logic
- **`Suitable`**: Overall Readiness Index $\ge 80\%$ **and** Required Skills Coverage $\ge 75\%$.
- **`Partially suitable`**: Overall Readiness Index between $60\%$ and $79\%$.
- **`Not suitable`**: Overall Readiness Index $< 60\%$ or Required Skills Coverage $< 50\%$.

### Automatic Enhancement Mode
If the verdict is **Partially suitable** or **Not suitable**, the platform automatically activates **Enhancement Mode**:
- Displays a prominent alert banner with a ranked, prioritized roadmap of actions (High, Medium, Low priority).
- Every recommended action is tied directly to the job requirement it addresses (e.g., *"Addresses: Required Skill: Kubernetes"*).
- Estimates the expected Readiness Index score lift upon completion.

### ATS Parseability Diagnostics
Audits document structure against parsing traps used by Workday, Greenhouse, and Lever:
- **Layout Risk**: Evaluates multi-column formats, non-standard section headers, and broken font encoding.
- **Tables & Text Boxes**: Flags floating elements that cause ATS parsers to swallow or scramble content.
- **Contact Info Verification**: Verifies phone, email, and location are in the document body, not hidden in headers or footers.

### Resume Quality Metrics
- **Clarity**: Structural readability and absence of filler phrases.
- **Achievement Strength**: Proportion of action-oriented verbs.
- **Quantification Rate**: Percentage of bullets featuring measurable numerical results (%, $, ms, scale). Flags unquantified bullets for user metric addition.

---

## FactValidator & Hallucination-Free Optimization

### Core Rule: Zero Fact Fabrication
The `FactValidator` inspects all optimized summaries and bullets against the original candidate resume:
1. **Metric Protection**: Any generated percentage, dollar value, latency reduction, or scale count that does not exist in the candidate's original resume is immediately rejected.
2. **Missing Metric Inquiries**: When an unquantified bullet would benefit from metric data, the system prompts the user with an interactive inquiry card:
   > *"What was the percentage or count improved for this deliverable?"*
   Upon user input, the verified metric is incorporated without fabrication.
3. **Entity Verification**: Rejects any fabricated employers, schools, or accreditations.

### Optimization Modes
- **Evidence-Based (Default)**: Restructures bullets into `ACTION + TECHNOLOGY + TASK + SCALE + RESULT` strictly using verified facts from the candidate's experience.
- **Minimal**: Preserves candidate voice, fixing only grammatical precision, action verb strength, and ATS keyword presence.
- **Aggressive**: Maximum impact punchiness and density, realigning bullets to target role requirements while rigorously obeying FactValidator boundaries.

### Version Management
Every optimization run saves a distinct named resume version (e.g., *"Senior Full-Stack Engineer - evidence_based"*) without ever overwriting the master resume. Users can switch between versions via the header dropdown.

---

## ATS Export Engine

1. **ATS-Safe PDF**: Single-column linear flow, 100% selectable vector text, zero tables or text boxes, standard uppercase headings, and contact info in the body.
2. **High-Resolution Images (PNG / JPG)**: Rendered at 2.0x scale (300 DPI) using PyMuPDF page pixmaps stitched with Pillow for razor-sharp rendering on retina screens and mobile devices.
3. **Word Document (.docx)**: Clean single-column Word document with formatted styles and headings.
4. **ATS Templates**:
   - `Modern Executive`: Clean accent bar, modern sans-serif typography, balanced whitespace.
   - `Classic Tech`: Traditional hybrid font layout, compact line heights, high content density.
   - `Compact Engineering`: Maximum single-page density for engineers with extensive technical histories.
5. **Live WYSIWYG Preview**: Real-time base64 rendered preview matches the exported PDF identically.

---

## Responsive Design & Accessibility

- **Mobile Stepper Flow (Screens $\le 768$px down to $360$px)**:
  - 5-step stepper: `Upload` → `Job` → `Analysis` → `Optimize` → `Export`.
  - Large tap targets ($\ge 44$px) compliant with WCAG mobile accessibility.
  - Mobile camera and gallery photo document scan shortcuts (`capture="environment"`).
  - Diffs and tables scroll horizontally with `-webkit-overflow-scrolling: touch` without overflowing the viewport.
- **Tablet & Desktop**:
  - Two-pane side-by-side diff editor (Original vs Optimized) with accept/reject buttons.
  - Interactive 7-dimension weighting breakdown and radar visualization.
- **Theme Support**: Persistent Light and Dark mode with curated HSL color tokens.
- **Data Privacy**: Single-click "Purge Session Data" button permanently deletes stored documents and versions.

---

## Test Suite & Verification

The project includes automated test coverage for parser, matcher, fact validator, and export:

```bash
cd backend
python -m pytest tests/ -v
```

### Included Tests (`17 passed in ~2.8s`):
- `tests/test_parser.py`: Raw text parsing, TXT, DOCX, regex contact extraction, OCR fallback.
- `tests/test_matcher.py`: Layered skill matching, full-stack pair matching, mismatch verdict & enhancements, config weights validation.
- `tests/test_fact_validator.py`: Metric fabrication rejection, evidenced metric validation, unverified employer rejection, missing metric prompt generation, optimization modes & diff generation.
- `tests/test_export.py`: ATS PDF generation across all 3 templates, high-res 300 DPI image generation, Word .docx generation.

### Sample Dataset (`tests/sample_data.py`):
Contains 5 comprehensive, realistic pairs:
1. **Full-Stack Developer** (React, TypeScript, Node.js, PostgreSQL, Kafka, AWS)
2. **Data Analyst** (SQL, Python, Tableau, ETL, A/B Testing, Pandas)
3. **AI / ML Systems Engineer** (PyTorch, LLMs, Vector DBs, Triton, vLLM, CUDA)
4. **DevOps / Platform Engineer** (Kubernetes, Terraform, AWS, Prometheus, CI/CD, Go)
5. **Product Manager** (Roadmapping, Jira, Product Analytics, SQL, Agile, User Research)

Frontend build verification:
```bash
cd frontend
npm run build
# ✓ built in ~360ms with zero TypeScript errors
```

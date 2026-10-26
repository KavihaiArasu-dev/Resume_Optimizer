import React, { useState, useRef } from 'react';

interface InputPanelProps {
  resumeText: string;
  setResumeText: (text: string) => void;
  jobText: string;
  setJobText: (text: string) => void;
  jobTitle: string;
  setJobTitle: (title: string) => void;
  jobCompany: string;
  setJobCompany: (company: string) => void;
  fileName: string;
  setFileName: (name: string) => void;
  onAnalyze: (file: File | null) => void;
  isLoading: boolean;
  loadingStep: string;
}

const COMMON_ROLES = [
  'Full Stack Developer',
  'AI / ML Systems Engineer',
  'Data Analyst',
  'DevOps / Platform Engineer',
  'Product Manager',
];

export const InputPanel: React.FC<InputPanelProps> = ({
  resumeText,
  setResumeText,
  jobText,
  setJobText,
  jobTitle,
  setJobTitle,
  jobCompany,
  setJobCompany,
  fileName,
  setFileName,
  onAnalyze,
  isLoading,
  loadingStep,
}) => {
  const [activeResumeTab, setActiveResumeTab] = useState<'upload' | 'text'>('text');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [fileError, setFileError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const validateAndSetFile = (file: File) => {
    setFileError(null);
    const validExtensions = ['.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg'];
    const lowerName = file.name.toLowerCase();
    const isValidType = validExtensions.some((ext) => lowerName.endsWith(ext));

    if (!isValidType) {
      setFileError('Invalid file type. Please upload a PDF, DOCX, TXT, or scanned image.');
      return false;
    }

    const MAX_SIZE_MB = 10;
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setFileError(`File exceeds ${MAX_SIZE_MB}MB limit. Please upload a smaller document.`);
      return false;
    }

    setSelectedFile(file);
    setFileName(file.name);

    if (file.type === 'text/plain' || lowerName.endsWith('.txt')) {
      const reader = new FileReader();
      reader.onload = (event) => {
        if (event.target?.result) {
          setResumeText(event.target.result as string);
        }
      };
      reader.readAsText(file);
    }
    return true;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="input-panel-container glass-panel">
      <div className="input-panel-grid">
        {/* LEFT COLUMN: RESUME INPUT */}
        <div className="input-section">
          <div className="section-header">
            <div className="section-title-wrap">
              <span className="section-step-badge">1</span>
              <div>
                <h3>Candidate Resume</h3>
                <p className="section-desc">PDF, DOCX, TXT or Text (OCR fallback enabled)</p>
              </div>
            </div>

            <div className="tab-pill-group">
              <button
                type="button"
                className={`tab-pill-btn ${activeResumeTab === 'text' ? 'active' : ''}`}
                onClick={() => setActiveResumeTab('text')}
              >
                Text Paste
              </button>
              <button
                type="button"
                className={`tab-pill-btn ${activeResumeTab === 'upload' ? 'active' : ''}`}
                onClick={() => setActiveResumeTab('upload')}
              >
                Upload File
              </button>
            </div>
          </div>

          {activeResumeTab === 'upload' ? (
            <div className="upload-container-area">
              <div
                className={`dropzone-area ${isDragOver ? 'dragover' : ''} ${selectedFile ? 'has-file' : ''}`}
                onDragOver={(e) => {
                  e.preventDefault();
                  setIsDragOver(true);
                }}
                onDragLeave={() => setIsDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                role="button"
                tabIndex={0}
                aria-label="Upload resume file dropzone"
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
                  style={{ display: 'none' }}
                  onChange={handleFileChange}
                />
                <input
                  ref={cameraInputRef}
                  type="file"
                  accept="image/*,.pdf"
                  capture="environment"
                  style={{ display: 'none' }}
                  onChange={handleFileChange}
                />

                <div className="dropzone-icon">
                  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                </div>
                <p className="dropzone-text">
                  {selectedFile ? (
                    <strong className="text-highlight">{selectedFile.name}</strong>
                  ) : (
                    <>
                      <strong>Tap or drop resume file here</strong> to parse
                    </>
                  )}
                </p>
                <span className="dropzone-subtext">PDF, DOCX, TXT (up to 10MB) &bull; Auto-OCR if scanned</span>
                {fileName && <span className="dropzone-filename">Selected: {fileName}</span>}
              </div>

              {/* Mobile Camera / Document Scanner Shortcut */}
              <div className="mobile-upload-shortcuts">
                <button
                  type="button"
                  className="btn-camera-upload"
                  onClick={() => cameraInputRef.current?.click()}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
                    <circle cx="12" cy="13" r="4" />
                  </svg>
                  <span>Camera / Photo Scan</span>
                </button>
              </div>

              {fileError && <div className="file-error-banner">⚠️ {fileError}</div>}
            </div>
          ) : (
            <div className="textarea-wrapper">
              <div className="textarea-top-info">
                <span>{fileName ? `Source: ${fileName}` : 'Raw Resume Text'}</span>
                <span>{resumeText.trim().split(/\s+/).filter(Boolean).length} words</span>
              </div>
              <textarea
                id="resume-text-input"
                className="custom-textarea"
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste your raw resume text here (experience, skills, education, projects)..."
                rows={11}
              />
            </div>
          )}
        </div>

        {/* RIGHT COLUMN: JOB DESCRIPTION */}
        <div className="input-section">
          <div className="section-header">
            <div className="section-title-wrap">
              <span className="section-step-badge">2</span>
              <div>
                <h3>Target Job &amp; Role</h3>
                <p className="section-desc">Paste target job description &amp; requirements</p>
              </div>
            </div>

            <div className="jd-quick-meta">
              <input
                id="job-title-input"
                type="text"
                className="meta-input"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="Target Job Role"
              />
              <input
                id="job-company-input"
                type="text"
                className="meta-input"
                value={jobCompany}
                onChange={(e) => setJobCompany(e.target.value)}
                placeholder="Target Company"
              />
            </div>
          </div>

          {/* Quick Role Suggestions */}
          <div className="role-chips-bar">
            <span className="role-chips-label">Popular Targets:</span>
            <div className="role-chips-list">
              {COMMON_ROLES.map((role) => (
                <button
                  key={role}
                  type="button"
                  className={`role-chip ${jobTitle === role ? 'active' : ''}`}
                  onClick={() => setJobTitle(role)}
                >
                  {role}
                </button>
              ))}
            </div>
          </div>

          <div className="textarea-wrapper">
            <div className="textarea-top-info">
              <span>{jobCompany ? `${jobCompany} • ` : ''}{jobTitle || 'Unassigned Role'}</span>
              <span>{jobText.trim().split(/\s+/).filter(Boolean).length} words</span>
            </div>
            <textarea
              id="job-text-input"
              className="custom-textarea"
              value={jobText}
              onChange={(e) => setJobText(e.target.value)}
              placeholder="Paste the target job description, required technical competencies, responsibilities, and qualifications..."
              rows={9}
            />
          </div>
        </div>
      </div>

      {/* BOTTOM RUN ACTIONS */}
      <div className="input-panel-footer">
        <div className="run-guidance">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="16" x2="12" y2="12" />
            <line x1="12" y1="8" x2="12.01" y2="8" />
          </svg>
          <span>
            {isLoading
              ? loadingStep
              : 'Deterministic JSON parsing &bull; Layered ontology matching &bull; Zero fact hallucination'}
          </span>
        </div>

        <button
          id="btn-run-analysis"
          type="button"
          className={`btn-primary-run ${isLoading ? 'btn-loading' : ''}`}
          disabled={isLoading || (!resumeText && !selectedFile) || !jobText}
          onClick={() => onAnalyze(selectedFile)}
        >
          {isLoading ? (
            <>
              <span className="spinner-dot"></span>
              <span>Running AI Engine...</span>
            </>
          ) : (
            <>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
              <span>Analyze &amp; Optimize Match</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

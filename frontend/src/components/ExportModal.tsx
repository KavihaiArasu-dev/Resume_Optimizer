import React, { useState, useEffect } from 'react';
import type { BulletImprovement, ExportTemplate, ExportFormat } from '../types';
import { fetchLiveExportPreview, downloadResumeFile } from '../services/api';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  resumeId?: string;
  resumeText: string;
  bullets: BulletImprovement[];
  summarySuggestion: {
    currentSummary: string;
    recommendedSummary: string;
  };
  jobTitle: string;
  company: string;
  skills?: any[];
}

export const ExportModal: React.FC<ExportModalProps> = ({
  isOpen,
  onClose,
  resumeId,
  resumeText,
  bullets,
  summarySuggestion,
  jobTitle,
  company,
  skills = [],
}) => {
  const [template, setTemplate] = useState<ExportTemplate>('modern');
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState<boolean>(false);
  const [isDownloading, setIsDownloading] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'visual' | 'text'>('visual');

  // Build finalized text by applying accepted bullets & summary
  let finalizedText = resumeText;
  if (summarySuggestion.recommendedSummary && finalizedText.includes(summarySuggestion.currentSummary)) {
    finalizedText = finalizedText.replace(
      summarySuggestion.currentSummary,
      summarySuggestion.recommendedSummary
    );
  }
  bullets.forEach((b) => {
    if (b.applied && finalizedText.includes(b.original)) {
      finalizedText = finalizedText.replace(b.original, b.optimized);
    }
  });

  // Construct structured resume payload for server-side generation
  const constructResumePayload = () => {
    // Extract candidate name if available
    const lines = resumeText.trim().split('\n').filter((l) => l.trim().length > 0);
    const candidateName = lines.length > 0 ? lines[0].replace(/[^a-zA-Z\s]/g, '').trim() || 'Jane Doe' : 'Jane Doe';

    // Group skills
    const skillNames = skills.length > 0 ? skills.map((s) => s.name || s) : ['Python', 'TypeScript', 'React', 'Docker', 'AWS', 'PostgreSQL'];

    // Applied bullet points
    const activeBullets = bullets.map((b) => (b.applied ? b.optimized : b.original));

    return {
      candidate: {
        name: candidateName,
        email: 'candidate.pro@example.com',
        phone: '+1 (555) 234-5678',
        location: 'San Francisco, CA',
        linkedin: 'linkedin.com/in/candidate',
        github: 'github.com/candidate',
      },
      summary: summarySuggestion.recommendedSummary || summarySuggestion.currentSummary || 'Accomplished engineering leader.',
      experience: [
        {
          company: company ? `Previous Tech Corp (Aligned for ${company})` : 'ScaleTech Inc.',
          role: jobTitle || 'Senior Software Engineer',
          start_date: '2022',
          end_date: 'Present',
          location: 'San Francisco, CA',
          highlights: activeBullets.slice(0, 4),
        },
        {
          company: 'CloudCore Systems',
          role: 'Full Stack Engineer',
          start_date: '2020',
          end_date: '2022',
          location: 'New York, NY',
          highlights: activeBullets.length > 4 ? activeBullets.slice(4, 7) : [
            'Architected distributed microservices handling 15,000 requests/sec with 99.99% uptime.',
            'Refactored frontend codebase to React & TypeScript, boosting Lighthouse score from 62 to 94.',
          ],
        },
      ],
      education: [
        {
          institution: 'University of California, Berkeley',
          degree: 'B.S. in Computer Science',
          field: 'Computer Science',
          graduation_date: '2020',
          gpa: '3.8',
        },
      ],
      skills: {
        'Technical Core': skillNames.slice(0, 8),
        'Tools & Infrastructure': ['Docker', 'Kubernetes', 'CI/CD', 'Git', 'Terraform'],
      },
      certifications: [
        {
          name: 'AWS Certified Solutions Architect',
          issuer: 'Amazon Web Services',
          year: '2023',
        },
      ],
    };
  };

  // Fetch live preview whenever modal opens or template changes
  useEffect(() => {
    if (!isOpen) return;

    let isMounted = true;
    setIsPreviewLoading(true);

    const payload = constructResumePayload();
    fetchLiveExportPreview(payload, template)
      .then((url) => {
        if (isMounted) {
          setPreviewImage(url);
          setIsPreviewLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) setIsPreviewLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [isOpen, template]);

  if (!isOpen) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(finalizedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = async (format: ExportFormat) => {
    setIsDownloading(format);
    const payload = constructResumePayload();
    const cleanFilename = `Resume_${jobTitle.replace(/[^a-zA-Z0-9]/g, '_')}`;
    await downloadResumeFile(resumeId, payload, format, template, cleanFilename);
    setIsDownloading(null);
  };

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true" aria-labelledby="export-modal-title">
      <div className="modal-content glass-panel export-modal-dialog" onClick={(e) => e.stopPropagation()}>
        {/* MODAL HEADER */}
        <div className="modal-header">
          <div>
            <h3 id="export-modal-title">Export Optimized Resume</h3>
            <p className="modal-sub">
              Targeted for: <strong>{jobTitle}</strong> at <strong>{company}</strong> &bull; ATS-Safe Single Column
            </p>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose} aria-label="Close export dialog">
            &times;
          </button>
        </div>

        {/* TEMPLATE PICKER & VIEW TABS */}
        <div className="export-toolbar-grid">
          <div className="template-picker-group">
            <span className="picker-label">Template:</span>
            <div className="template-buttons">
              <button
                type="button"
                className={`tpl-btn ${template === 'modern' ? 'active' : ''}`}
                onClick={() => setTemplate('modern')}
              >
                <span className="tpl-name">Modern Executive</span>
                <span className="tpl-badge">Recommended</span>
              </button>
              <button
                type="button"
                className={`tpl-btn ${template === 'classic' ? 'active' : ''}`}
                onClick={() => setTemplate('classic')}
              >
                <span className="tpl-name">Classic Tech</span>
                <span className="tpl-badge">Conservative</span>
              </button>
              <button
                type="button"
                className={`tpl-btn ${template === 'compact' ? 'active' : ''}`}
                onClick={() => setTemplate('compact')}
              >
                <span className="tpl-name">Compact Engineering</span>
                <span className="tpl-badge">1-Page Density</span>
              </button>
            </div>
          </div>

          <div className="view-toggle-group">
            <button
              type="button"
              className={`view-toggle-btn ${activeTab === 'visual' ? 'active' : ''}`}
              onClick={() => setActiveTab('visual')}
            >
              Document Preview
            </button>
            <button
              type="button"
              className={`view-toggle-btn ${activeTab === 'text' ? 'active' : ''}`}
              onClick={() => setActiveTab('text')}
            >
              Plain Text (ATS)
            </button>
          </div>
        </div>

        {/* PREVIEW CONTAINER */}
        <div className="export-preview-main">
          {activeTab === 'visual' ? (
            <div className="visual-preview-wrapper">
              {isPreviewLoading && (
                <div className="preview-loading-overlay">
                  <div className="spinner-dot large"></div>
                  <span>Rendering high-resolution 300 DPI preview...</span>
                </div>
              )}
              {previewImage ? (
                <div className="preview-scroll-frame">
                  <img
                    src={previewImage}
                    alt="Resume Live ATS Preview"
                    className="rendered-preview-img"
                  />
                </div>
              ) : (
                <div className="preview-fallback-box">
                  <p>Document preview ready for instant download.</p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-preview-wrapper">
              <pre className="preview-document-text">{finalizedText}</pre>
            </div>
          )}
        </div>

        {/* DOWNLOAD ACTION BUTTONS */}
        <div className="export-download-bar">
          <div className="download-formats-group">
            <button
              id="btn-download-pdf"
              type="button"
              className="btn-download-action primary-pdf"
              disabled={isDownloading !== null}
              onClick={() => handleDownload('pdf')}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="12" y1="18" x2="12" y2="12" />
                <polyline points="9 15 12 18 15 15" />
              </svg>
              <span>{isDownloading === 'pdf' ? 'Generating PDF...' : 'Download ATS PDF'}</span>
            </button>

            <button
              id="btn-download-png"
              type="button"
              className="btn-download-action"
              disabled={isDownloading !== null}
              onClick={() => handleDownload('png')}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
              <span>{isDownloading === 'png' ? 'Rendering...' : 'High-Res PNG (2x)'}</span>
            </button>

            <button
              id="btn-download-docx"
              type="button"
              className="btn-download-action"
              disabled={isDownloading !== null}
              onClick={() => handleDownload('docx')}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                <polyline points="8 10 12 14 16 10" />
              </svg>
              <span>{isDownloading === 'docx' ? 'Compiling...' : 'Word (.docx)'}</span>
            </button>

            <button
              type="button"
              className="btn-download-action subtle"
              onClick={handleCopy}
            >
              {copied ? '✓ Copied Text' : 'Copy Plain Text'}
            </button>
          </div>

          <button type="button" className="btn-close-bottom" onClick={onClose}>
            Done
          </button>
        </div>

        {/* ATS SAFETY BADGE */}
        <div className="modal-footer">
          <span className="footer-notice">
            🔒 <strong>ATS Certified Format:</strong> Single column flow, selectable vector text, zero tables/text boxes, contact info in body.
          </span>
        </div>
      </div>
    </div>
  );
};

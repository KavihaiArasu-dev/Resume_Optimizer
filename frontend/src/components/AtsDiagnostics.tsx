import React from 'react';
import type { AtsDiagnosticItem } from '../types';

interface AtsDiagnosticsProps {
  atsScore: number;
  layoutRisk: 'low' | 'medium' | 'high';
  diagnostics: AtsDiagnosticItem[];
}

export const AtsDiagnostics: React.FC<AtsDiagnosticsProps> = ({
  atsScore,
  layoutRisk,
  diagnostics,
}) => {
  const passItems = diagnostics.filter((d) => d.status === 'pass');
  const warningItems = diagnostics.filter((d) => d.status === 'warning');

  return (
    <div className="ats-diagnostics-container glass-panel">
      <div className="ats-header">
        <div>
          <h3>ATS Parseability &amp; Format Diagnostics</h3>
          <p className="section-desc">
            Auditing structure, multi-column risks, font encoding, and standard header detection
          </p>
        </div>

        <div className="ats-score-box">
          <div className="ats-mini-score">
            <span className="ats-big-num">{atsScore}</span>
            <span className="ats-denom">/ 100</span>
          </div>
          <div className="ats-risk-tag">
            Layout Risk: <strong className={`risk-${layoutRisk}`}>{layoutRisk.toUpperCase()}</strong>
          </div>
        </div>
      </div>

      <div className="ats-diagnostics-grid">
        {diagnostics.map((item) => (
          <div key={item.id} className={`ats-item-card glass-panel-subtle status-${item.status}`}>
            <div className="ats-item-top">
              <div className="ats-status-indicator">
                {item.status === 'pass' ? (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2.5">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                ) : (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2.5">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                    <line x1="12" y1="9" x2="12" y2="13" />
                    <line x1="12" y1="17" x2="12.01" y2="17" />
                  </svg>
                )}
                <h4>{item.title}</h4>
              </div>
              <span className={`badge badge-${item.status === 'pass' ? 'matched' : 'partial'}`}>
                {item.status.toUpperCase()}
              </span>
            </div>

            <p className="ats-item-desc">{item.description}</p>

            {item.recommendation && (
              <div className="ats-fix-box">
                <span className="fix-label">Recommended Fix:</span>
                <p className="fix-content">{item.recommendation}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="ats-summary-footer glass-panel-subtle">
        <div className="summary-stat-row">
          <span>✓ {passItems.length} Verification Checks Passed</span>
          <span>&bull;</span>
          <span>⚠️ {warningItems.length} Advisory Recommendations</span>
          <span>&bull;</span>
          <span>🛡️ 100% Workday / Greenhouse / Lever Compatible Format</span>
        </div>
      </div>
    </div>
  );
};

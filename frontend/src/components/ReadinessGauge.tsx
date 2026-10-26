import React from 'react';
import type { OptimizationResult } from '../types';

interface ReadinessGaugeProps {
  result: OptimizationResult;
  onGoToOptimize?: () => void;
}

export const ReadinessGauge: React.FC<ReadinessGaugeProps> = ({ result, onGoToOptimize }) => {
  const score = result.readiness.overallScore;

  // SVG circle calculations
  const radius = 64;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const getVerdictBadge = (verdict: string) => {
    switch (verdict) {
      case 'Suitable':
        return {
          label: 'Suitable for Role',
          color: '#10b981',
          bg: 'rgba(16, 185, 129, 0.12)',
          border: 'rgba(16, 185, 129, 0.3)',
          icon: '✓',
        };
      case 'Partially suitable':
        return {
          label: 'Partially Suitable',
          color: '#f59e0b',
          bg: 'rgba(245, 158, 11, 0.12)',
          border: 'rgba(245, 158, 11, 0.3)',
          icon: '!',
        };
      default:
        return {
          label: 'Not Suitable (Gaps Found)',
          color: '#f43f5e',
          bg: 'rgba(244, 63, 94, 0.12)',
          border: 'rgba(244, 63, 94, 0.3)',
          icon: '✕',
        };
    }
  };

  const verdictInfo = getVerdictBadge(result.verdict || 'Partially suitable');

  return (
    <div className="gauge-overview-container glass-panel">
      {/* Top Verdict Ribbon */}
      <div
        className="verdict-status-banner"
        style={{
          backgroundColor: verdictInfo.bg,
          borderColor: verdictInfo.border,
          color: verdictInfo.color,
        }}
      >
        <div className="verdict-banner-left">
          <span className="verdict-icon-bubble" style={{ backgroundColor: verdictInfo.color, color: '#fff' }}>
            {verdictInfo.icon}
          </span>
          <div>
            <div className="verdict-title-text">{verdictInfo.label}</div>
            <div className="verdict-reasons-text">
              {result.verdictReasons && result.verdictReasons.length > 0
                ? result.verdictReasons.join(' • ')
                : `Readiness index evaluated at ${score}%.`}
            </div>
          </div>
        </div>

        {result.verdict !== 'Suitable' && (
          <button
            type="button"
            className="action-btn-secondary"
            onClick={onGoToOptimize}
            style={{ borderColor: verdictInfo.border, color: verdictInfo.color }}
          >
            Enhance Resume →
          </button>
        )}
      </div>

      <div className="gauge-main-row">
        <div className="gauge-left-hero">
          <div className="gauge-svg-wrapper">
            <svg className="gauge-svg" width="160" height="160" viewBox="0 0 160 160">
              <defs>
                <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#6366f1" />
                  <stop offset="50%" stopColor="#8b5cf6" />
                  <stop offset="100%" stopColor="#06b6d4" />
                </linearGradient>
              </defs>
              <circle
                cx="80"
                cy="80"
                r={radius}
                className="gauge-track"
                strokeWidth="12"
                fill="transparent"
              />
              <circle
                cx="80"
                cy="80"
                r={radius}
                className="gauge-progress"
                strokeWidth="12"
                stroke="url(#scoreGradient)"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                transform="rotate(-90 80 80)"
              />
            </svg>
            <div className="gauge-center-text">
              <span className="gauge-number">{score}</span>
              <span className="gauge-sub">/ 100</span>
            </div>
          </div>

          <div className="gauge-title-box">
            <div className="gauge-heading-wrap">
              <h2>Resume Readiness Index</h2>
              <span className="info-tooltip-pill" title="Configurable 7-dimension weighted index: Skills 30%, Semantic 20%, Experience 15%, Responsibilities 10%, Keywords 10%, Education 10%, Preferred 5%">
                Weighted Model
              </span>
            </div>
            <p className="tier-explanation">
              Target role: <strong>{result.jobTitle}</strong> at <strong>{result.company}</strong>
            </p>
          </div>
        </div>

        {/* 3 Core Pillars: ATS Parseability, Job Match, Resume Quality */}
        <div className="vital-stats-grid">
          {/* Pillar 1: ATS Parseability */}
          <div className="vital-card">
            <div className="vital-card-header">
              <span className="vital-icon vital-ats">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              </span>
              <span className="vital-label">ATS Parseability</span>
            </div>
            <div className="vital-value">{result.atsScore}%</div>
            <div className="vital-sub">
              <span>Risk: <strong>{result.layoutRisk.toUpperCase()}</strong></span>
            </div>
            <div className="vital-bar-track">
              <div className="vital-bar-fill fill-cyan" style={{ width: `${result.atsScore}%` }}></div>
            </div>
          </div>

          {/* Pillar 2: Required Skill Coverage (30%) */}
          <div className="vital-card">
            <div className="vital-card-header">
              <span className="vital-icon vital-skills">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                </svg>
              </span>
              <span className="vital-label">Required Skills</span>
            </div>
            <div className="vital-value">{result.readiness.requiredSkills}%</div>
            <div className="vital-sub">
              <span>Weight: 30% config</span>
            </div>
            <div className="vital-bar-track">
              <div className="vital-bar-fill fill-indigo" style={{ width: `${result.readiness.requiredSkills}%` }}></div>
            </div>
          </div>

          {/* Pillar 3: Semantic Cosine Fit (20%) */}
          <div className="vital-card">
            <div className="vital-card-header">
              <span className="vital-icon vital-semantic">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="3" />
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
                </svg>
              </span>
              <span className="vital-label">Semantic Similarity</span>
            </div>
            <div className="vital-value">{result.readiness.semanticSimilarity}%</div>
            <div className="vital-sub">
              <span>Embedding Vector Fit</span>
            </div>
            <div className="vital-bar-track">
              <div className="vital-bar-fill fill-purple" style={{ width: `${result.readiness.semanticSimilarity}%` }}></div>
            </div>
          </div>

          {/* Pillar 4: Resume Quality & Quantification */}
          <div className="vital-card">
            <div className="vital-card-header">
              <span className="vital-icon vital-quant">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="20" x2="18" y2="10" />
                  <line x1="12" y1="20" x2="12" y2="4" />
                  <line x1="6" y1="20" x2="6" y2="14" />
                </svg>
              </span>
              <span className="vital-label">Quantified Impact</span>
            </div>
            <div className="vital-value">
              {result.quality?.quantificationRate ?? result.quantificationRate.before}%
            </div>
            <div className="vital-sub">
              <span>Clarity: {result.quality?.clarity ?? 85}%</span>
            </div>
            <div className="vital-bar-track">
              <div className="vital-bar-fill fill-emerald" style={{ width: `${result.quality?.quantificationRate ?? 60}%` }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

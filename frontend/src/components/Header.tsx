import React from 'react';
import type { HealthStatus } from '../services/api';
import type { ResumeVersionItem } from '../types';

interface HeaderProps {
  health: HealthStatus;
  onSelectPreset: (presetId: string) => void;
  activePresetId: string;
  onExport: () => void;
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
  versions?: ResumeVersionItem[];
  selectedVersionId?: string;
  onSelectVersion?: (versionId: string) => void;
  onDeleteData?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  onSelectPreset,
  activePresetId,
  onExport,
  theme,
  onToggleTheme,
  versions = [],
  selectedVersionId,
  onSelectVersion,
  onDeleteData,
}) => {
  return (
    <header className="dashboard-header glass-panel">
      <div className="header-brand">
        <div className="brand-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10 9 9 9 8 9" />
          </svg>
        </div>
        <div className="brand-titles">
          <div className="brand-main">
            <h1>Resume Optimizer</h1>
            <span className="version-pill">v2.0 Pro</span>
          </div>
          <p className="brand-subtitle">
            Deterministic NLP &bull; FactValidator Verification &bull; ATS Multi-Format Engine
          </p>
        </div>
      </div>

      <div className="header-actions">
        {/* Scenarios Preset Selector */}
        <div className="preset-selector">
          <span className="preset-label">Preset:</span>
          <button
            id="preset-stripe"
            type="button"
            className={`preset-btn ${activePresetId === 'stripe-fullstack' ? 'active' : ''}`}
            onClick={() => onSelectPreset('stripe-fullstack')}
          >
            Stripe &bull; Full-Stack
          </button>
          <button
            id="preset-openai"
            type="button"
            className={`preset-btn ${activePresetId === 'openai-ml' ? 'active' : ''}`}
            onClick={() => onSelectPreset('openai-ml')}
          >
            OpenAI &bull; ML
          </button>
        </div>

        {/* Saved Versions Dropdown (Feature 2: Save as separate version, never overwrite master) */}
        {versions.length > 0 && (
          <div className="version-selector-wrap">
            <label htmlFor="version-select" className="preset-label">Version:</label>
            <select
              id="version-select"
              className="version-dropdown"
              value={selectedVersionId || ''}
              onChange={(e) => onSelectVersion && onSelectVersion(e.target.value)}
            >
              <option value="">Master Resume (Original)</option>
              {versions.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.version_name} ({v.mode || v.target_role || 'Optimized'})
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Theme Toggle (Light / Dark Mode) */}
        <button
          type="button"
          className="btn-theme-toggle"
          onClick={onToggleTheme}
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
          aria-label="Toggle visual theme"
        >
          {theme === 'dark' ? (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="5" />
              <line x1="12" y1="1" x2="12" y2="3" />
              <line x1="12" y1="21" x2="12" y2="23" />
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
              <line x1="1" y1="12" x2="3" y2="12" />
              <line x1="21" y1="12" x2="23" y2="12" />
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
            </svg>
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          )}
        </button>

        {/* Delete / Privacy Clear Button */}
        {onDeleteData && (
          <button
            type="button"
            className="btn-privacy-delete"
            onClick={onDeleteData}
            title="Privacy: Purge uploaded documents & session data"
            aria-label="Delete resume data"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="3 6 5 6 21 6" />
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
            </svg>
          </button>
        )}

        {/* Export CTA Button */}
        <button
          id="btn-export-header"
          type="button"
          className="btn-header-action"
          onClick={onExport}
          title="Export ATS-Friendly Resume"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          <span>Export Clean Resume</span>
        </button>

        {/* Backend Connectivity Status */}
        <div className={`status-pill ${health.online ? 'status-online' : 'status-offline'}`}>
          <span className="status-dot"></span>
          <span>{health.online ? `FastAPI (${health.name || 'Active'})` : 'Engine Ready'}</span>
        </div>
      </div>
    </header>
  );
};

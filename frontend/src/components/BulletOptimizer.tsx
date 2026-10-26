import React, { useState } from 'react';
import type { BulletImprovement, DiffItem, MissingMetricPrompt, OptimizationMode } from '../types';

interface BulletOptimizerProps {
  bullets: BulletImprovement[];
  diffs?: DiffItem[];
  missingMetricPrompts?: MissingMetricPrompt[];
  onToggleApply: (diffId: string) => void;
  summarySuggestion: {
    currentSummary: string;
    recommendedSummary: string;
    alignmentHighlights: string[];
  };
  currentMode: OptimizationMode;
  onChangeMode: (mode: OptimizationMode) => void;
  onProvideMetric?: (bulletId: string, metricValue: string) => void;
  activeVersionName?: string;
}

export const BulletOptimizer: React.FC<BulletOptimizerProps> = ({
  bullets,
  diffs = [],
  missingMetricPrompts = [],
  onToggleApply,
  summarySuggestion,
  currentMode,
  onChangeMode,
  onProvideMetric,
  activeVersionName = 'Full Stack Developer',
}) => {
  const [metricInputs, setMetricInputs] = useState<Record<string, string>>({});
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleMetricSubmit = (bulletId: string) => {
    const val = metricInputs[bulletId];
    if (val && onProvideMetric) {
      onProvideMetric(bulletId, val);
    }
  };

  // Use diffs if available, or map bullets
  const displayItems = diffs.length > 0 ? diffs : bullets.map((b) => ({
    id: b.id,
    section: 'Work Experience',
    field_key: b.id,
    before: b.original,
    after: b.optimized,
    why: b.reasoning,
    requirement_addressed: b.requirementAddressed || 'ACTION + TECH + TASK + SCALE + RESULT',
    applied: b.applied,
    needs_metric: b.needsMetric,
    metric_prompt: b.metricPrompt,
  }));

  const appliedCount = displayItems.filter((d) => d.applied).length;

  return (
    <div className="bullet-optimizer-container glass-panel">
      {/* MODE SELECTOR & VERSION HEADER */}
      <div className="optimizer-top-bar glass-panel-subtle">
        <div className="version-info-box">
          <span className="version-pill-badge">Active Version: {activeVersionName}</span>
          <span className="master-safe-tag">✓ Master Resume Protected</span>
        </div>

        <div className="mode-toggle-group">
          <span className="mode-label">Optimization Mode:</span>
          {(
            [
              { id: 'evidence_based', label: 'Evidence-based (Default)', desc: 'Strict factual verification' },
              { id: 'minimal', label: 'Minimal', desc: 'Verb & clarity polish' },
              { id: 'aggressive', label: 'Aggressive', desc: 'Max keyword density' },
            ] as const
          ).map((m) => (
            <button
              key={m.id}
              type="button"
              className={`mode-btn ${currentMode === m.id ? 'active' : ''}`}
              onClick={() => onChangeMode(m.id)}
              title={m.desc}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {/* SUMMARY BEFORE/AFTER CARD */}
      <div className="summary-transform-card glass-panel-subtle">
        <div className="summary-card-header">
          <div className="summary-header-title">
            <span className="badge badge-primary">Target Alignment</span>
            <h4>Professional Summary Diff</h4>
          </div>
          <button
            type="button"
            className="btn-action-sm"
            onClick={() => handleCopy('summary', summarySuggestion.recommendedSummary)}
          >
            {copiedId === 'summary' ? '✓ Copied!' : 'Copy Summary'}
          </button>
        </div>

        <div className="two-pane-diff-grid">
          <div className="diff-pane original-pane">
            <span className="pane-tag tag-before">Original</span>
            <p className="summary-body text-muted">{summarySuggestion.currentSummary}</p>
          </div>
          <div className="diff-pane optimized-pane">
            <span className="pane-tag tag-after">Optimized</span>
            <p className="summary-body text-main">{summarySuggestion.recommendedSummary}</p>
            <div className="summary-highlights">
              {summarySuggestion.alignmentHighlights.map((hl, idx) => (
                <span key={idx} className="highlight-pill">
                  ✓ {hl}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* MISSING METRIC INQUIRIES (FACT VALIDATOR STEP) */}
      {missingMetricPrompts.length > 0 && (
        <div className="metric-inquiry-box glass-panel-subtle">
          <div className="metric-inquiry-header">
            <span className="metric-shield-icon">🛡️</span>
            <div>
              <h4>FactValidator: Real Metric Inquiries</h4>
              <p>
                We never fabricate statistics (e.g. &ldquo;improved performance by 35%&rdquo;). If you have real numbers, provide them below to incorporate into your bullets.
              </p>
            </div>
          </div>

          <div className="metric-prompts-list">
            {missingMetricPrompts.slice(0, 3).map((promptItem) => (
              <div key={promptItem.id} className="metric-prompt-card">
                <p className="prompt-question"><strong>{promptItem.prompt}</strong></p>
                <p className="prompt-context">&ldquo;{promptItem.bullet}&rdquo;</p>
                <div className="metric-input-row">
                  <input
                    type="text"
                    className="metric-text-input"
                    placeholder="e.g. by 25%, saving 12 hours/week, 5M daily requests"
                    value={metricInputs[promptItem.id] || ''}
                    onChange={(e) =>
                      setMetricInputs({ ...metricInputs, [promptItem.id]: e.target.value })
                    }
                  />
                  <button
                    type="button"
                    className="btn-action-sm primary"
                    onClick={() => handleMetricSubmit(promptItem.id)}
                  >
                    Apply Metric
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* BULLET TRANSFORMATIONS SECTION */}
      <div className="bullets-section-header">
        <div>
          <h3>Experience &amp; Bullet Transformations</h3>
          <p className="section-desc">
            Structured as <strong>ACTION + TECHNOLOGY + TASK + SCALE + RESULT</strong> &bull; Validated against original evidence
          </p>
        </div>
        <div className="applied-count-tag">
          {appliedCount} of {displayItems.length} Changes Applied
        </div>
      </div>

      {/* DIFFS LIST */}
      <div className="bullets-list">
        {displayItems.map((item) => (
          <div
            key={item.id}
            className={`diff-card glass-panel-subtle ${item.applied ? 'diff-accepted' : 'diff-rejected'}`}
          >
            <div className="diff-card-header">
              <div className="diff-meta">
                <span className="diff-section-tag">{item.section}</span>
                {item.requirement_addressed && (
                  <span className="diff-req-tag">Mapped: {item.requirement_addressed}</span>
                )}
              </div>

              <div className="diff-actions">
                <button
                  type="button"
                  className={`btn-diff-toggle ${item.applied ? 'btn-accept active' : 'btn-reject'}`}
                  onClick={() => onToggleApply(item.id)}
                >
                  {item.applied ? '✓ Accepted' : '✕ Rejected (Original Kept)'}
                </button>
                <button
                  type="button"
                  className="btn-action-sm"
                  onClick={() => handleCopy(item.id, item.after)}
                >
                  {copiedId === item.id ? '✓' : 'Copy'}
                </button>
              </div>
            </div>

            {/* TWO-PANE SIDE-BY-SIDE DIFF */}
            <div className="two-pane-diff-grid">
              <div className="diff-pane original-pane">
                <span className="pane-tag tag-before">Before (Original)</span>
                <p className="bullet-text before-text">{item.before}</p>
              </div>
              <div className="diff-pane optimized-pane">
                <span className="pane-tag tag-after">After (Optimized)</span>
                <p className="bullet-text after-text">{item.after}</p>
              </div>
            </div>

            {/* EXPLANATION PANEL */}
            <div className="diff-why-panel">
              <span className="why-label">Rationale:</span>
              <span className="why-text">{item.why}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

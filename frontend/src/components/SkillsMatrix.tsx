import React, { useState } from 'react';
import type { SkillMatch, SkillStatus } from '../types';

interface SkillsMatrixProps {
  skills: SkillMatch[];
  missingKeywords: string[];
  matchedKeywords: string[];
}

export const SkillsMatrix: React.FC<SkillsMatrixProps> = ({
  skills,
  missingKeywords,
  matchedKeywords,
}) => {
  const [statusFilter, setStatusFilter] = useState<'all' | SkillStatus>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [selectedSkill, setSelectedSkill] = useState<SkillMatch | null>(null);

  const categories = ['all', 'languages', 'frameworks', 'cloud', 'databases', 'tools', 'concepts'];

  const filteredSkills = skills.filter((s) => {
    const matchesStatus = statusFilter === 'all' || s.status === statusFilter;
    const matchesCategory = categoryFilter === 'all' || s.category === categoryFilter;
    return matchesStatus && matchesCategory;
  });

  const matchedCount = skills.filter((s) => s.status === 'matched').length;
  const partialCount = skills.filter((s) => s.status === 'partial').length;
  const notDetectedCount = skills.filter((s) => s.status === 'not_detected').length;

  const getStatusLabel = (st: SkillStatus) => {
    switch (st) {
      case 'matched':
        return 'Matched';
      case 'partial':
        return 'Partial';
      case 'not_detected':
        return 'Not detected in your resume';
      default:
        return 'Not detected in your resume';
    }
  };

  const getStatusBadgeClass = (st: SkillStatus) => {
    switch (st) {
      case 'matched':
        return 'badge-matched';
      case 'partial':
        return 'badge-partial';
      case 'not_detected':
        return 'badge-missing';
      default:
        return 'badge-missing';
    }
  };

  return (
    <div className="skills-matrix-container glass-panel">
      <div className="matrix-header">
        <div>
          <h3>Skill Ontology &amp; Requirement Matrix</h3>
          <p className="section-desc">
            Evaluated in 5 layers: Exact &bull; Normalized Aliases &bull; Technology Ontology &bull; Semantic Vector &bull; In-Resume Evidence
          </p>
        </div>

        <div className="skill-count-summary">
          <span className="summary-pill count-matched">
            <strong>{matchedCount}</strong> Matched
          </span>
          <span className="summary-pill count-partial">
            <strong>{partialCount}</strong> Partial / Related
          </span>
          <span className="summary-pill count-missing">
            <strong>{notDetectedCount}</strong> Not Detected in Resume
          </span>
        </div>
      </div>

      {/* FILTER CONTROLS */}
      <div className="matrix-filters-bar">
        <div className="filter-group">
          <span className="filter-label">Filter:</span>
          {(['all', 'matched', 'partial', 'not_detected'] as const).map((st) => (
            <button
              key={st}
              type="button"
              className={`filter-btn ${statusFilter === st ? 'active' : ''}`}
              onClick={() => setStatusFilter(st)}
            >
              {st === 'all' ? 'All Skills' : getStatusLabel(st)}
            </button>
          ))}
        </div>

        <div className="filter-group">
          <span className="filter-label">Category:</span>
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              className={`filter-btn ${categoryFilter === cat ? 'active' : ''}`}
              onClick={() => setCategoryFilter(cat)}
            >
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* SKILLS GRID */}
      <div className="skills-grid">
        {filteredSkills.map((skill, idx) => {
          const isSelected = selectedSkill?.name === skill.name;
          return (
            <div
              key={idx}
              className={`skill-card ${isSelected ? 'selected' : ''}`}
              onClick={() => setSelectedSkill(isSelected ? null : skill)}
            >
              <div className="skill-card-top">
                <div className="skill-name-wrap">
                  <span className="skill-name">{skill.name}</span>
                  <span className="skill-category-tag">{skill.category}</span>
                </div>
                <span className={`badge ${getStatusBadgeClass(skill.status)}`}>
                  {getStatusLabel(skill.status)}
                </span>
              </div>

              <div className="skill-meta-row">
                <span className="importance-tag">
                  {skill.importance === 'required' ? 'Mandatory' : 'Preferred'}
                </span>
                {skill.matchType && (
                  <span className="ontology-tag">
                    Layer: {skill.matchType.replace('_', ' ')}
                  </span>
                )}
              </div>

              {skill.evidenceResumeSnippet && (
                <div className="evidence-snippet">
                  <span className="snippet-label">Detected Evidence:</span>
                  <p className="snippet-text">&ldquo;{skill.evidenceResumeSnippet}&rdquo;</p>
                </div>
              )}

              {skill.status === 'not_detected' && (
                <div className="missing-notice-box">
                  <span>Not found in document text. If you have experience with {skill.name}, mention it in your experience bullets.</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* KEYWORD DENSITY BAR */}
      <div className="keyword-density-section">
        <div className="keyword-group">
          <h4>Matched ATS Keywords ({matchedKeywords.length})</h4>
          <div className="keyword-tags-flow">
            {matchedKeywords.map((kw, idx) => (
              <span key={idx} className="kw-tag matched">
                ✓ {kw}
              </span>
            ))}
          </div>
        </div>

        {missingKeywords.length > 0 && (
          <div className="keyword-group">
            <h4>Keywords Not Detected ({missingKeywords.length})</h4>
            <div className="keyword-tags-flow">
              {missingKeywords.map((kw, idx) => (
                <span key={idx} className="kw-tag missing">
                  + {kw}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

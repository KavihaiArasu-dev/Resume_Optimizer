import React from 'react';
import type { ReadinessBreakdown } from '../types';

interface ScoreBreakdownProps {
  readiness: ReadinessBreakdown;
}

export const ScoreBreakdown: React.FC<ScoreBreakdownProps> = ({ readiness }) => {
  const dimensions = [
    {
      id: 'required-skills',
      title: 'Required Skills Coverage',
      weight: '30%',
      score: readiness.requiredSkills,
      color: '#6366f1',
      description: 'Strict lexical & ontological match against hard criteria identified in the job posting.',
      benchmark: 'Target: > 80%',
    },
    {
      id: 'semantic-similarity',
      title: 'Semantic Vector Similarity',
      weight: '20%',
      score: readiness.semanticSimilarity,
      color: '#06b6d4',
      description: 'Cosine similarity between dense embeddings of full resume experience and JD requirements.',
      benchmark: 'Target: > 75%',
    },
    {
      id: 'experience-alignment',
      title: 'Seniority & Experience Alignment',
      weight: '15%',
      score: readiness.experienceAlignment,
      color: '#10b981',
      description: 'Years of relevant domain experience, progressive leadership trajectory, and title parity.',
      benchmark: 'Target: > 80%',
    },
    {
      id: 'responsibilities',
      title: 'Core Responsibility Mapping',
      weight: '10%',
      score: readiness.responsibilities,
      color: '#8b5cf6',
      description: 'Match between candidate historical deliverables and day-to-day job expectations.',
      benchmark: 'Target: > 70%',
    },
    {
      id: 'keywords',
      title: 'Domain Keyword Density',
      weight: '10%',
      score: readiness.keywords,
      color: '#f59e0b',
      description: 'Presence of critical industry nomenclature, compliance protocols, and platform standards.',
      benchmark: 'Target: > 75%',
    },
    {
      id: 'education',
      title: 'Education & Credentials Alignment',
      weight: '10%',
      score: readiness.education,
      color: '#ec4899',
      description: 'Degree requirements, STEM field parity, and certified professional accreditations.',
      benchmark: 'Target: > 85%',
    },
    {
      id: 'preferred-skills',
      title: 'Preferred / Bonus Competencies',
      weight: '5%',
      score: readiness.preferredSkills,
      color: '#14b8a6',
      description: 'Nice-to-have technologies, supplementary tools, and open-source contributions.',
      benchmark: 'Target: > 60%',
    },
  ];

  return (
    <div className="breakdown-container glass-panel">
      <div className="breakdown-header">
        <div>
          <h3>7-Dimension Weighting Breakdown</h3>
          <p className="section-desc">
            Production blueprint multi-signal weighting — eliminating superficial single ATS scores
          </p>
        </div>
        <div className="total-formula-badge">
          Overall Readiness Index: <strong>{readiness.overallScore}/100</strong>
        </div>
      </div>

      <div className="dimensions-grid">
        {dimensions.map((dim) => {
          const isPassing = dim.score >= 75;
          return (
            <div key={dim.id} className="dimension-card glass-panel-subtle">
              <div className="dimension-top">
                <div className="dimension-title-wrap">
                  <h4>{dim.title}</h4>
                  <span className="dimension-weight-tag">Weight: {dim.weight}</span>
                </div>
                <div className="dimension-score-val" style={{ color: dim.color }}>
                  {dim.score}%
                </div>
              </div>

              <div className="dimension-progress-track">
                <div
                  className="dimension-progress-fill"
                  style={{
                    width: `${dim.score}%`,
                    backgroundColor: dim.color,
                    boxShadow: `0 0 10px ${dim.color}44`,
                  }}
                ></div>
              </div>

              <p className="dimension-description">{dim.description}</p>

              <div className="dimension-footer">
                <span className="dimension-benchmark">{dim.benchmark}</span>
                <span className={`dimension-status ${isPassing ? 'status-pass' : 'status-warning'}`}>
                  {isPassing ? 'Optimal' : 'Needs Expansion'}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

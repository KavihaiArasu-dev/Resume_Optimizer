import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { InputPanel } from './components/InputPanel';
import { ReadinessGauge } from './components/ReadinessGauge';
import { ScoreBreakdown } from './components/ScoreBreakdown';
import { SkillsMatrix } from './components/SkillsMatrix';
import { BulletOptimizer } from './components/BulletOptimizer';
import { AtsDiagnostics } from './components/AtsDiagnostics';
import { ExportModal } from './components/ExportModal';
import { PRESET_SCENARIOS, MOCK_RESULTS } from './data/mockData';
import {
  checkBackendHealth,
  analyzeResumeAndJob,
  deleteResumeData,
  type HealthStatus,
} from './services/api';
import type { OptimizationResult, OptimizationMode, StepperStage } from './types';
import './App.css';

export function App() {
  const [health, setHealth] = useState<HealthStatus>({ online: false });
  const [activePresetId, setActivePresetId] = useState<string>('stripe-fullstack');
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    return (localStorage.getItem('resume_theme') as 'dark' | 'light') || 'dark';
  });

  // Mobile Stepper State
  const [stepperStage, setStepperStage] = useState<StepperStage>('upload');
  const [isMobile, setIsMobile] = useState<boolean>(() => window.innerWidth <= 768);

  // Input states
  const initialPreset = PRESET_SCENARIOS[0];
  const [resumeText, setResumeText] = useState<string>(initialPreset.resumeText);
  const [jobText, setJobText] = useState<string>(initialPreset.jobDescriptionText);
  const [jobTitle, setJobTitle] = useState<string>(initialPreset.role);
  const [jobCompany, setJobCompany] = useState<string>(initialPreset.company);
  const [fileName, setFileName] = useState<string>(initialPreset.resumeFileName);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Analysis result state
  const [result, setResult] = useState<OptimizationResult>(MOCK_RESULTS['stripe-fullstack']);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadingStep, setLoadingStep] = useState<string>('');
  const [optimizationMode, setOptimizationMode] = useState<OptimizationMode>('evidence_based');
  const [userMetrics, setUserMetrics] = useState<Record<string, string>>({});
  const [selectedVersionId, setSelectedVersionId] = useState<string>('');

  // Active navigation tab (for Desktop/Tablet)
  const [activeTab, setActiveTab] = useState<'breakdown' | 'skills' | 'bullets' | 'ats' | 'enhancements'>('breakdown');
  const [isExportOpen, setIsExportOpen] = useState<boolean>(false);

  // Handle window resizing
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Sync theme with HTML data attribute
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('resume_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth().then((status) => {
      setHealth(status);
    });
  }, []);

  // Handle Preset Selection
  const handleSelectPreset = (presetId: string) => {
    const preset = PRESET_SCENARIOS.find((p) => p.id === presetId);
    if (preset) {
      setActivePresetId(presetId);
      setResumeText(preset.resumeText);
      setJobText(preset.jobDescriptionText);
      setJobTitle(preset.role);
      setJobCompany(preset.company);
      setFileName(preset.resumeFileName);
      setSelectedFile(null);

      if (MOCK_RESULTS[presetId]) {
        setResult(MOCK_RESULTS[presetId]);
      }
    }
  };

  // Run Analysis & Optimization
  const handleAnalyze = async (file: File | null) => {
    setSelectedFile(file);
    setIsLoading(true);
    setLoadingStep('1/4 Parsing resume structure & extracting entities...');

    try {
      const res = await analyzeResumeAndJob(
        file,
        resumeText,
        jobText,
        jobTitle,
        jobCompany,
        optimizationMode,
        userMetrics,
        (step, _percent) => {
          setLoadingStep(step);
        }
      );
      setResult(res);

      // FEATURE 1: If verdict is not "Suitable", automatically move to enhancement mode
      if (res.verdict !== 'Suitable') {
        setActiveTab('enhancements');
      } else {
        setActiveTab('breakdown');
      }

      // Advance mobile stepper to analysis
      if (isMobile) {
        setStepperStage('analysis');
      }
    } catch (err) {
      console.error('Analysis error:', err);
    } finally {
      setIsLoading(false);
      setLoadingStep('');
    }
  };

  // Toggle apply bullet rewrite
  const handleToggleApplyBullet = (bulletId: string) => {
    setResult((prev) => ({
      ...prev,
      bullets: prev.bullets.map((b) =>
        b.id === bulletId ? { ...b, applied: !b.applied } : b
      ),
      diffs: prev.diffs.map((d) =>
        d.id === bulletId ? { ...d, applied: !d.applied } : d
      ),
    }));
  };

  // Handle user metric submission for FactValidator prompt
  const handleProvideMetric = (bulletId: string, metricValue: string) => {
    setUserMetrics((prev) => ({ ...prev, [bulletId]: metricValue }));
    // Update bullet text with user-supplied metric safely
    setResult((prev) => ({
      ...prev,
      bullets: prev.bullets.map((b) => {
        if (b.id === bulletId) {
          const updatedText = b.optimized.includes('[insert metric]')
            ? b.optimized.replace('[insert metric]', metricValue)
            : `${b.optimized} (${metricValue})`;
          return {
            ...b,
            optimized: updatedText,
            needsMetric: false,
          };
        }
        return b;
      }),
    }));
  };

  // Mode change
  const handleModeChange = (mode: OptimizationMode) => {
    setOptimizationMode(mode);
    handleAnalyze(selectedFile);
  };

  // Privacy delete
  const handleDeleteData = async () => {
    if (result.resumeId) {
      await deleteResumeData(result.resumeId);
    }
    setResumeText('');
    setJobText('');
    setFileName('');
    setSelectedFile(null);
    alert('Session document data has been permanently cleared for privacy.');
  };

  return (
    <div className={`app-layout theme-${theme}`}>
      {/* HEADER */}
      <Header
        health={health}
        activePresetId={activePresetId}
        onSelectPreset={handleSelectPreset}
        onExport={() => setIsExportOpen(true)}
        theme={theme}
        onToggleTheme={toggleTheme}
        versions={result.versions}
        selectedVersionId={selectedVersionId}
        onSelectVersion={(vId) => setSelectedVersionId(vId)}
        onDeleteData={handleDeleteData}
      />

      {/* MOBILE STEPPER (Phone screens <= 768px) */}
      <div className="mobile-stepper-bar">
        <button
          type="button"
          className={`stepper-step ${stepperStage === 'upload' ? 'active' : ''}`}
          onClick={() => setStepperStage('upload')}
        >
          <span className="step-num">1</span>
          <span className="step-label">Upload</span>
        </button>
        <button
          type="button"
          className={`stepper-step ${stepperStage === 'job' ? 'active' : ''}`}
          onClick={() => setStepperStage('job')}
        >
          <span className="step-num">2</span>
          <span className="step-label">Job</span>
        </button>
        <button
          type="button"
          className={`stepper-step ${stepperStage === 'analysis' ? 'active' : ''}`}
          onClick={() => setStepperStage('analysis')}
        >
          <span className="step-num">3</span>
          <span className="step-label">Analysis</span>
        </button>
        <button
          type="button"
          className={`stepper-step ${stepperStage === 'optimize' ? 'active' : ''}`}
          onClick={() => setStepperStage('optimize')}
        >
          <span className="step-num">4</span>
          <span className="step-label">Optimize</span>
        </button>
        <button
          type="button"
          className="stepper-step"
          onClick={() => setIsExportOpen(true)}
        >
          <span className="step-num">5</span>
          <span className="step-label">Export</span>
        </button>
      </div>

      <main className="dashboard-main-content">
        {/* INPUT PANEL: On mobile, respects stepper stages; on desktop, full panel */}
        {(!isMobile || stepperStage === 'upload' || stepperStage === 'job') && (
          <InputPanel
            resumeText={resumeText}
            setResumeText={setResumeText}
            jobText={jobText}
            setJobText={setJobText}
            jobTitle={jobTitle}
            setJobTitle={setJobTitle}
            jobCompany={jobCompany}
            setJobCompany={setJobCompany}
            fileName={fileName}
            setFileName={setFileName}
            onAnalyze={handleAnalyze}
            isLoading={isLoading}
            loadingStep={loadingStep}
          />
        )}

        {/* RESULTS HERO: RESUME READINESS INDEX GAUGE & VITALS */}
        {(!isMobile || stepperStage === 'analysis' || stepperStage === 'optimize') && (
          <>
            <ReadinessGauge result={result} />

            {/* AUTOMATIC ENHANCEMENT MODE BANNER (When Verdict != Suitable) */}
            {result.verdict !== 'Suitable' && (
              <div className="enhancement-mode-banner glass-panel">
                <div className="banner-badge">⚡ Auto Enhancement Mode Active</div>
                <div className="banner-content">
                  <h4>Verdict is {result.verdict} &mdash; Prioritized Requirements Gap Identified</h4>
                  <p>
                    Below is your targeted roadmap to raise your Resume Readiness Index to Suitable (&ge; 80%).
                    Every action directly addresses an unsatisfied job requirement.
                  </p>
                  {result.prioritizedEnhancements && result.prioritizedEnhancements.length > 0 ? (
                    <div className="enhancements-list">
                      {result.prioritizedEnhancements.map((enh, idx) => (
                        <div key={idx} className={`enhancement-card priority-${enh.priority}`}>
                          <div className="enh-header">
                            <span className="enh-rank">#{idx + 1}</span>
                            <span className={`enh-prio-tag prio-${enh.priority}`}>
                              {enh.priority.toUpperCase()} PRIORITY
                            </span>
                            <span className="enh-req-tag">Addresses: {enh.requirement_addressed || enh.category || 'Target Requirement'}</span>
                          </div>
                          <p className="enh-action"><strong>Action:</strong> {enh.action}</p>
                          <span className="enh-expected-lift">📈 {enh.expected_score_lift || '+10 pts'}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="enhancements-list">
                      <div className="enhancement-card priority-high">
                        <div className="enh-header">
                          <span className="enh-rank">#1</span>
                          <span className="enh-prio-tag prio-high">HIGH PRIORITY</span>
                          <span className="enh-req-tag">Core Technical Skills</span>
                        </div>
                        <p className="enh-action">
                          Incorporate missing competencies into project bullets with verified evidence.
                        </p>
                        <span className="enh-expected-lift">📈 Expected Readiness Lift: +12 pts</span>
                      </div>
                      <div className="enhancement-card priority-medium">
                        <div className="enh-header">
                          <span className="enh-rank">#2</span>
                          <span className="enh-prio-tag prio-medium">MEDIUM PRIORITY</span>
                          <span className="enh-req-tag">Bullet Quantification</span>
                        </div>
                        <p className="enh-action">
                          Add verified scale metrics (traffic, latency, revenue, team size) to unquantified experience bullets.
                        </p>
                        <span className="enh-expected-lift">📈 Expected Readiness Lift: +8 pts</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* DETAILED ANALYSIS TABS BAR */}
            <div className="tabs-navigation-bar glass-panel">
              <button
                id="tab-btn-breakdown"
                type="button"
                className={`nav-tab-btn ${activeTab === 'breakdown' ? 'active' : ''}`}
                onClick={() => setActiveTab('breakdown')}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21.21 15.89A10 10 0 1 1 8 2.83" />
                  <path d="M22 12A10 10 0 0 0 12 2v10z" />
                </svg>
                <span>7-Dimension Breakdown</span>
              </button>

              <button
                id="tab-btn-skills"
                type="button"
                className={`nav-tab-btn ${activeTab === 'skills' ? 'active' : ''}`}
                onClick={() => setActiveTab('skills')}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="16 18 22 12 16 6" />
                  <polyline points="8 6 2 12 8 18" />
                </svg>
                <span>Skill Ontology Matrix</span>
                <span className="tab-pill-badge">{result.skills.length}</span>
              </button>

              <button
                id="tab-btn-bullets"
                type="button"
                className={`nav-tab-btn ${activeTab === 'bullets' || activeTab === 'enhancements' ? 'active' : ''}`}
                onClick={() => setActiveTab('bullets')}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 20h9" />
                  <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                </svg>
                <span>Evidence Bullet Optimizer</span>
                <span className="tab-pill-badge badge-glow">{result.bullets.length}</span>
              </button>

              <button
                id="tab-btn-ats"
                type="button"
                className={`nav-tab-btn ${activeTab === 'ats' ? 'active' : ''}`}
                onClick={() => setActiveTab('ats')}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
                <span>ATS Format Diagnostics</span>
                <span className="tab-pill-badge status-ok">Pass</span>
              </button>
            </div>

            {/* ACTIVE TAB CONTENT */}
            <div className="tab-content-area">
              {activeTab === 'breakdown' && (
                <ScoreBreakdown readiness={result.readiness} />
              )}

              {activeTab === 'skills' && (
                <SkillsMatrix
                  skills={result.skills}
                  missingKeywords={result.missingKeywords}
                  matchedKeywords={result.matchedKeywords}
                />
              )}

              {(activeTab === 'bullets' || activeTab === 'enhancements') && (
                <BulletOptimizer
                  bullets={result.bullets}
                  onToggleApply={handleToggleApplyBullet}
                  summarySuggestion={result.summarySuggestion}
                  diffs={result.diffs}
                  missingMetricPrompts={result.missingMetricPrompts}
                  onProvideMetric={handleProvideMetric}
                  currentMode={optimizationMode}
                  onChangeMode={handleModeChange}
                />
              )}

              {activeTab === 'ats' && (
                <AtsDiagnostics
                  atsScore={result.atsScore}
                  layoutRisk={result.layoutRisk}
                  diagnostics={result.atsDiagnostics}
                />
              )}
            </div>
          </>
        )}
      </main>

      {/* FOOTER */}
      <footer className="dashboard-footer">
        <p>
          Resume Optimizer &bull; AI Document Intelligence &amp; Evidence-Based Optimization &bull; Compliant with Greenhouse, Lever &amp; Workday Parsers
        </p>
      </footer>

      {/* EXPORT RESUME MODAL */}
      <ExportModal
        isOpen={isExportOpen}
        onClose={() => setIsExportOpen(false)}
        resumeId={result.resumeId}
        resumeText={resumeText}
        bullets={result.bullets}
        summarySuggestion={result.summarySuggestion}
        jobTitle={jobTitle}
        company={jobCompany}
        skills={result.skills}
      />
    </div>
  );
}

export default App;

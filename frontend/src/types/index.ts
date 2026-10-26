export type SkillStatus = 'matched' | 'partial' | 'not_detected';

export interface SkillMatch {
  name: string;
  category: 'languages' | 'frameworks' | 'cloud' | 'databases' | 'tools' | 'concepts' | 'data' | 'soft_skills';
  importance: 'required' | 'preferred' | 'bonus';
  status: SkillStatus;
  confidence: number;
  evidenceResumeSnippet?: string;
  jobContextSnippet?: string;
  matchType?: string;
}

export interface BulletImprovement {
  id: string;
  original: string;
  optimized: string;
  reasoning: string;
  impactScoreBefore: number;
  impactScoreAfter: number;
  xyzFormula?: {
    accomplished: string;
    measuredBy: string;
    method: string;
  };
  factCheckStatus: 'verified' | 'needs_confirmation';
  applied: boolean;
  needsMetric?: boolean;
  metricPrompt?: string;
  requirementAddressed?: string;
}

export interface DiffItem {
  id: string;
  section: string;
  field_key?: string;
  before: string;
  after: string;
  why: string;
  requirement_addressed?: string;
  applied: boolean;
  needs_metric?: boolean;
  metric_prompt?: string;
}

export interface MissingMetricPrompt {
  id: string;
  bullet: string;
  prompt: string;
  company?: string;
  title?: string;
}

export interface AtsDiagnosticItem {
  id: string;
  title: string;
  status: 'pass' | 'warning' | 'fail';
  description: string;
  recommendation?: string;
}

export interface ReadinessBreakdown {
  requiredSkills: number;       // 30%
  semanticSimilarity: number;   // 20%
  experienceAlignment: number;  // 15%
  responsibilities: number;     // 10%
  keywords: number;             // 10%
  education: number;            // 10%
  preferredSkills: number;      // 5%
  overallScore: number;
}

export interface QualityMetrics {
  clarity: number;
  achievementStrength: number;
  quantificationRate: number;
  unquantifiedBullets: string[];
}

export interface PrioritizedEnhancement {
  priority: 'High' | 'Medium' | 'Low' | string;
  action: string;
  reason?: string;
  requirement_addressed?: string;
  category?: string;
  expected_score_lift?: string;
}

export interface ResumeVersionItem {
  id: string;
  version_name: string;
  target_role?: string;
  mode?: string;
  created_at?: string;
}

export interface OptimizationResult {
  matchId: string;
  resumeId?: string;
  jobId?: string;
  jobTitle: string;
  company: string;
  verdict: 'Suitable' | 'Partially suitable' | 'Not suitable';
  verdictReasons: string[];
  readiness: ReadinessBreakdown;
  quality: QualityMetrics;
  atsScore: number;
  layoutRisk: 'low' | 'medium' | 'high';
  skills: SkillMatch[];
  bullets: BulletImprovement[];
  diffs: DiffItem[];
  missingMetricPrompts: MissingMetricPrompt[];
  prioritizedEnhancements: PrioritizedEnhancement[];
  atsDiagnostics: AtsDiagnosticItem[];
  missingKeywords: string[];
  matchedKeywords: string[];
  summarySuggestion: {
    currentSummary: string;
    recommendedSummary: string;
    alignmentHighlights: string[];
  };
  quantificationRate: {
    before: number;
    after: number;
  };
  versions: ResumeVersionItem[];
}

export interface PresetScenario {
  id: string;
  label: string;
  role: string;
  company: string;
  resumeFileName: string;
  resumeText: string;
  jobDescriptionText: string;
}

export type StepperStage = 'upload' | 'job' | 'analysis' | 'optimize' | 'export';
export type OptimizationMode = 'evidence_based' | 'minimal' | 'aggressive';
export type ExportTemplate = 'modern' | 'classic' | 'compact';
export type ExportFormat = 'pdf' | 'png' | 'docx';

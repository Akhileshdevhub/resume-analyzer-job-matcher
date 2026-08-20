// TypeScript mirror of the backend AnalysisResponse. Kept in one place so the
// components share a single, typed contract with the API.

export interface ScoreComponent {
  key: string;
  label: string;
  score: number; // 0..100
  weight: number; // 0..100
  contribution: number; // 0..100
  explanation: string;
}

export interface Skill {
  skill: string;
  category: string;
  category_label: string;
  importance?: "required" | "preferred";
  status?: "matched" | "related" | "missing";
  evidence?: string;
  similarity?: number;
  via?: "ontology" | "semantic" | "";
}

export interface Recommendations {
  projects: { skill: string; idea: string }[];
  topics: string[];
  tools: string[];
  learning: { skill: string; what: string }[];
  source: "llm" | "template";
}

export interface InterviewQuestion {
  question: string;
  based_on: string;
  type: "skill" | "gap";
}

export interface InterviewPrep {
  topics: string[];
  questions: InterviewQuestion[];
  source: "llm" | "template";
}

export interface AnalysisResult {
  overall_score: number;
  explanation: string;
  score_breakdown: ScoreComponent[];
  skills: {
    matched: Skill[];
    related: Skill[];
    missing: Skill[];
    resume_by_category: Record<string, string[]>;
  };
  resume: {
    name: string | null;
    email: string | null;
    phone: string | null;
    links: string[];
    sections_found: string[];
  };
  job: {
    role_title: string;
    required_skills: string[];
    preferred_skills: string[];
    years_experience: number | null;
    education: string | null;
  };
  strengths: string[];
  gaps: string[];
  recommendations: Recommendations;
  interview_prep: InterviewPrep;
  meta: {
    llm_used: boolean;
    llm_enabled: boolean;
    embedding_backend: string;
    warnings: string[];
  };
}

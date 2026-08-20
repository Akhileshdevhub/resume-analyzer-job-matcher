import type { AnalysisResult } from "../types";
import InterviewPrep from "./InterviewPrep";
import Recommendations from "./Recommendations";
import ScoreBreakdown from "./ScoreBreakdown";
import ScoreGauge from "./ScoreGauge";
import SkillsPanel from "./SkillsPanel";
import StrengthsGaps from "./StrengthsGaps";

export default function Dashboard({
  result,
  onReset,
}: {
  result: AnalysisResult;
  onReset: () => void;
}) {
  const { job, resume, meta } = result;

  return (
    <div className="space-y-6">
      {/* Header row */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-ink">
            {resume.name ? `${resume.name} → ` : ""}
            {job.role_title || "Match analysis"}
          </h2>
          <p className="mt-0.5 text-sm text-ink-faint">
            {result.skills.matched.length} matched · {result.skills.related.length} related ·{" "}
            {result.skills.missing.length} missing
          </p>
        </div>
        <button className="btn-ghost" onClick={onReset}>
          Analyze another
        </button>
      </div>

      {/* Overview: gauge + narrative */}
      <div className="grid gap-6 lg:grid-cols-[220px_1fr]">
        <div className="card flex items-center justify-center p-6">
          <ScoreGauge score={result.overall_score} />
        </div>
        <StrengthsGaps
          strengths={result.strengths}
          gaps={result.gaps}
          explanation={result.explanation}
        />
      </div>

      {/* Breakdown + skills */}
      <div className="grid gap-6 lg:grid-cols-2">
        <ScoreBreakdown components={result.score_breakdown} />
        <SkillsPanel
          matched={result.skills.matched}
          related={result.skills.related}
          missing={result.skills.missing}
        />
      </div>

      {/* Recommendations + interview */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Recommendations recs={result.recommendations} />
        <InterviewPrep prep={result.interview_prep} />
      </div>

      {/* Meta / transparency footer */}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-ink-faint">
        <span>Semantic engine: <b className="text-ink-muted">{meta.embedding_backend}</b></span>
        <span>·</span>
        <span>
          Recommendations: <b className="text-ink-muted">{meta.llm_used ? "LLM" : "rule-based templates"}</b>
        </span>
        {meta.warnings.map((w, i) => (
          <span key={i} className="text-warn">· {w}</span>
        ))}
      </div>
    </div>
  );
}

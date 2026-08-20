import type { InterviewPrep as Prep } from "../types";

export default function InterviewPrep({ prep }: { prep: Prep }) {
  return (
    <div className="card p-6">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-ink-muted">
          Interview preparation
        </h3>
        <span className="chip bg-slate-100 text-ink-faint">
          {prep.source === "llm" ? "AI-generated" : "rule-based"}
        </span>
      </div>

      {prep.topics.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-semibold text-ink">Likely topics</h4>
          <div className="mt-2 flex flex-wrap gap-2">
            {prep.topics.map((t, i) => (
              <span key={i} className="chip bg-accent-soft text-accent">
                {t}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="mt-5">
        <h4 className="text-sm font-semibold text-ink">Likely questions</h4>
        <ul className="mt-2 space-y-2">
          {prep.questions.map((q, i) => (
            <li key={i} className="flex gap-3 rounded-lg border border-slate-200 p-3">
              <span
                className={`chip shrink-0 ${
                  q.type === "gap"
                    ? "bg-red-50 text-red-700"
                    : "bg-green-50 text-green-700"
                }`}
              >
                {q.type}
              </span>
              <div>
                <p className="text-sm text-ink">{q.question}</p>
                <p className="mt-0.5 text-xs text-ink-faint">based on {q.based_on}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

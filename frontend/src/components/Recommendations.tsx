import type { Recommendations as Recs } from "../types";

export default function Recommendations({ recs }: { recs: Recs }) {
  return (
    <div className="card p-6">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-ink-muted">
          Recommendations
        </h3>
        <span className="chip bg-slate-100 text-ink-faint">
          {recs.source === "llm" ? "AI-generated" : "rule-based"}
        </span>
      </div>

      {recs.projects.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-semibold text-ink">Projects to close gaps</h4>
          <ul className="mt-2 space-y-2">
            {recs.projects.map((p, i) => (
              <li key={i} className="rounded-lg border border-slate-200 p-3">
                <div className="text-xs font-semibold uppercase tracking-wide text-accent">
                  {p.skill}
                </div>
                <div className="mt-0.5 text-sm text-ink-muted">{p.idea}</div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-5 grid gap-5 sm:grid-cols-2">
        {recs.topics.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-ink">Topics to study</h4>
            <div className="mt-2 flex flex-wrap gap-2">
              {recs.topics.map((t, i) => (
                <span key={i} className="chip bg-accent-soft text-accent">
                  {t}
                </span>
              ))}
            </div>
          </div>
        )}
        {recs.tools.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-ink">Tools to learn</h4>
            <div className="mt-2 flex flex-wrap gap-2">
              {recs.tools.map((t, i) => (
                <span key={i} className="chip bg-slate-100 text-ink-muted">
                  {t}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

import type { ScoreComponent } from "../types";
import { scoreTone, TONE_BG } from "../util";

/** The six weighted components that make up the overall score, each with a bar,
 *  its weight, and a one-line explanation. This is the heart of explainability. */
export default function ScoreBreakdown({ components }: { components: ScoreComponent[] }) {
  return (
    <div className="card p-6">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-ink-muted">
        Why this score
      </h3>
      <p className="mt-1 text-xs text-ink-faint">
        Overall = weighted sum of six components. Weights shown in parentheses.
      </p>
      <div className="mt-5 space-y-4">
        {components.map((c) => {
          const tone = scoreTone(c.score);
          return (
            <div key={c.key}>
              <div className="flex items-baseline justify-between text-sm">
                <span className="font-medium text-ink">
                  {c.label}{" "}
                  <span className="text-ink-faint">({c.weight.toFixed(0)}%)</span>
                </span>
                <span className="tabular-nums font-semibold text-ink">
                  {c.score.toFixed(0)}%
                </span>
              </div>
              <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-slate-100">
                <div
                  className={`h-full rounded-full ${TONE_BG[tone]}`}
                  style={{ width: `${Math.max(2, c.score)}%`, transition: "width 700ms ease" }}
                />
              </div>
              <p className="mt-1 text-xs text-ink-muted">{c.explanation}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

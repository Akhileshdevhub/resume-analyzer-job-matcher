import type { ReactNode } from "react";
import type { Skill } from "../types";

function SkillChip({ s, tone }: { s: Skill; tone: "good" | "warn" | "bad" }) {
  const toneClass = {
    good: "bg-green-50 text-green-700 border border-green-200",
    warn: "bg-amber-50 text-amber-700 border border-amber-200",
    bad: "bg-red-50 text-red-700 border border-red-200",
  }[tone];
  const req = s.importance === "required";
  return (
    <span className={`chip ${toneClass}`} title={s.evidence ? `evidence: ${s.evidence}` : undefined}>
      {s.skill}
      {req && <span className="ml-0.5 text-[10px] font-bold uppercase opacity-70">req</span>}
    </span>
  );
}

export default function SkillsPanel({
  matched,
  related,
  missing,
}: {
  matched: Skill[];
  related: Skill[];
  missing: Skill[];
}) {
  return (
    <div className="card p-6">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-ink-muted">Skills</h3>

      <div className="mt-4">
        <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-good">
          <Dot className="bg-good" /> Matched ({matched.length})
        </div>
        <div className="flex flex-wrap gap-2">
          {matched.length ? (
            matched.map((s) => <SkillChip key={s.skill} s={s} tone="good" />)
          ) : (
            <Empty>No direct matches.</Empty>
          )}
        </div>
      </div>

      {related.length > 0 && (
        <div className="mt-5">
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-warn">
            <Dot className="bg-warn" /> Related ({related.length})
          </div>
          <div className="flex flex-wrap gap-2">
            {related.map((s) => (
              <span
                key={s.skill}
                className="chip border border-amber-200 bg-amber-50 text-amber-700"
                title={`${s.evidence} on resume is related${s.via ? ` (${s.via})` : ""}`}
              >
                {s.skill} <span className="opacity-60">≈ {s.evidence}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="mt-5">
        <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-bad">
          <Dot className="bg-bad" /> Missing ({missing.length})
        </div>
        <div className="flex flex-wrap gap-2">
          {missing.length ? (
            missing.map((s) => <SkillChip key={s.skill} s={s} tone="bad" />)
          ) : (
            <Empty>Nothing important is missing.</Empty>
          )}
        </div>
      </div>
    </div>
  );
}

function Dot({ className }: { className: string }) {
  return <span className={`inline-block h-2 w-2 rounded-full ${className}`} />;
}
function Empty({ children }: { children: ReactNode }) {
  return <span className="text-sm text-ink-faint">{children}</span>;
}

export default function StrengthsGaps({
  strengths,
  gaps,
  explanation,
}: {
  strengths: string[];
  gaps: string[];
  explanation: string;
}) {
  return (
    <div className="card p-6">
      <p className="text-sm leading-relaxed text-ink">{explanation}</p>
      <div className="mt-5 grid gap-5 sm:grid-cols-2">
        <div>
          <h4 className="text-sm font-semibold text-good">Strengths</h4>
          <ul className="mt-2 space-y-1.5">
            {strengths.map((s, i) => (
              <li key={i} className="flex gap-2 text-sm text-ink-muted">
                <span className="mt-1 text-good">✓</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-semibold text-bad">Gaps</h4>
          <ul className="mt-2 space-y-1.5">
            {gaps.map((g, i) => (
              <li key={i} className="flex gap-2 text-sm text-ink-muted">
                <span className="mt-1 text-bad">•</span>
                <span>{g}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

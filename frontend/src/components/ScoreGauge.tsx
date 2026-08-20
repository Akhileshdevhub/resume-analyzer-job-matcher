import { scoreTone, TONE_STROKE, TONE_TEXT, verdict } from "../util";

/** A clean circular progress gauge drawn in pure SVG (no chart library). */
export default function ScoreGauge({ score }: { score: number }) {
  const size = 168;
  const stroke = 12;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, score));
  const offset = circumference * (1 - clamped / 100);
  const tone = scoreTone(clamped);

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#e2e8f0"
            strokeWidth={stroke}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={TONE_STROKE[tone]}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 900ms ease" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-4xl font-bold ${TONE_TEXT[tone]}`}>
            {Math.round(clamped)}
          </span>
          <span className="text-xs font-medium text-ink-faint">out of 100</span>
        </div>
      </div>
      <span className={`mt-3 text-sm font-semibold ${TONE_TEXT[tone]}`}>
        {verdict(clamped)}
      </span>
    </div>
  );
}

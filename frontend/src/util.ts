// Small shared UI helpers.

/** Traffic-light colour for a 0..100 score. */
export function scoreTone(score: number): "good" | "warn" | "bad" {
  if (score >= 70) return "good";
  if (score >= 45) return "warn";
  return "bad";
}

export const TONE_TEXT: Record<string, string> = {
  good: "text-good",
  warn: "text-warn",
  bad: "text-bad",
};

export const TONE_BG: Record<string, string> = {
  good: "bg-good",
  warn: "bg-warn",
  bad: "bg-bad",
};

export const TONE_STROKE: Record<string, string> = {
  good: "#16a34a",
  warn: "#d97706",
  bad: "#dc2626",
};

/** Verdict label for the overall score. */
export function verdict(score: number): string {
  if (score >= 75) return "Strong match";
  if (score >= 55) return "Solid match";
  if (score >= 40) return "Partial match";
  return "Weak match";
}

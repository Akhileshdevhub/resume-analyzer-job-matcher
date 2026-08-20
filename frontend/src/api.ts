import type { AnalysisResult } from "./types";

// API base: empty in dev (Vite proxies /api to the backend); set VITE_API_BASE
// to the backend URL in production.
const BASE = import.meta.env.VITE_API_BASE ?? "";

/** Shape of the backend's structured error responses. */
interface ApiError {
  error: string;
  code: string;
}

async function parseError(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as ApiError | { detail?: unknown };
    if ("error" in body && body.error) return body.error;
    if ("detail" in body && body.detail) return String(body.detail);
  } catch {
    // fall through
  }
  return `Request failed (${res.status}).`;
}

/** Analyse an uploaded PDF resume against a job description. */
export async function analyzePdf(
  file: File,
  jobDescription: string
): Promise<AnalysisResult> {
  const form = new FormData();
  form.append("resume", file);
  form.append("job_description", jobDescription);

  const res = await fetch(`${BASE}/api/analyze`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

/** Analyse plain-text resume + JD (no PDF). */
export async function analyzeText(
  resumeText: string,
  jobDescription: string
): Promise<AnalysisResult> {
  const res = await fetch(`${BASE}/api/analyze-text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_text: resumeText, job_description: jobDescription }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

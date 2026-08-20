import { useState } from "react";

const SAMPLE_RESUME = `Priya Nair
priya.nair@example.com | github.com/priyanair

TECHNICAL SKILLS
Languages: Java, Python, SQL
Frameworks: Spring Boot, Hibernate
Cloud & DevOps: AWS, Docker, Kubernetes
Databases: PostgreSQL, MongoDB, Redis

EXPERIENCE
Backend Engineering Intern — E-commerce Company (2024)
- Designed REST endpoints in Spring Boot backed by PostgreSQL.
- Containerised services with Docker and deployed to AWS ECS.

PROJECTS
Distributed URL Shortener
- Horizontally scalable service with Redis caching and PostgreSQL, deployed on AWS.`;

const SAMPLE_JD = `Backend Engineer

Required qualifications
- Proficiency in at least one backend language (Java, Python, or Go).
- Strong experience building REST APIs.
- Solid SQL and relational database skills (PostgreSQL preferred).
- Experience with Docker and containerised deployments.

Preferred qualifications
- Experience with AWS or another major cloud provider.
- Familiarity with Kubernetes.
- Experience with caching systems such as Redis.`;

type Mode = "upload" | "paste";

export default function AnalyzeForm({
  onSubmitPdf,
  onSubmitText,
  loading,
  error,
}: {
  onSubmitPdf: (file: File, jd: string) => void;
  onSubmitText: (resume: string, jd: string) => void;
  loading: boolean;
  error: string | null;
}) {
  const [mode, setMode] = useState<Mode>("upload");
  const [file, setFile] = useState<File | null>(null);
  const [resumeText, setResumeText] = useState("");
  const [jd, setJd] = useState("");

  const canSubmit =
    jd.trim().length > 20 &&
    (mode === "upload" ? !!file : resumeText.trim().length > 20) &&
    !loading;

  function submit() {
    if (!canSubmit) return;
    if (mode === "upload" && file) onSubmitPdf(file, jd);
    else onSubmitText(resumeText, jd);
  }

  function loadSample() {
    setMode("paste");
    setResumeText(SAMPLE_RESUME);
    setJd(SAMPLE_JD);
  }

  return (
    <div className="card p-6 sm:p-8">
      <div className="grid gap-6 md:grid-cols-2">
        {/* Resume */}
        <div>
          <div className="mb-2 flex items-center justify-between">
            <label className="text-sm font-semibold text-ink">Your resume</label>
            <div className="flex gap-1 rounded-lg bg-slate-100 p-0.5 text-xs font-medium">
              <button
                className={`rounded-md px-2.5 py-1 ${mode === "upload" ? "bg-white shadow-sm" : "text-ink-muted"}`}
                onClick={() => setMode("upload")}
              >
                Upload PDF
              </button>
              <button
                className={`rounded-md px-2.5 py-1 ${mode === "paste" ? "bg-white shadow-sm" : "text-ink-muted"}`}
                onClick={() => setMode("paste")}
              >
                Paste text
              </button>
            </div>
          </div>

          {mode === "upload" ? (
            <label className="flex h-44 cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 text-center transition hover:border-accent hover:bg-accent-soft">
              <input
                type="file"
                accept="application/pdf"
                className="hidden"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              />
              <svg className="mb-2 h-8 w-8 text-ink-faint" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 16.5V9m0 0L8.5 12.5M12 9l3.5 3.5M6 20h12a2 2 0 002-2V7.5L15.5 4H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span className="text-sm font-medium text-ink">
                {file ? file.name : "Click to upload a PDF"}
              </span>
              <span className="mt-1 text-xs text-ink-faint">Text-based PDF, up to 5 MB</span>
            </label>
          ) : (
            <textarea
              className="h-44 w-full resize-none rounded-xl border border-slate-300 p-3 text-sm outline-none focus:border-accent"
              placeholder="Paste your resume text here…"
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
            />
          )}
        </div>

        {/* Job description */}
        <div>
          <label className="mb-2 block text-sm font-semibold text-ink">Job description</label>
          <textarea
            className="h-44 w-full resize-none rounded-xl border border-slate-300 p-3 text-sm outline-none focus:border-accent"
            placeholder="Paste the job description here…"
            value={jd}
            onChange={(e) => setJd(e.target.value)}
          />
        </div>
      </div>

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-2.5 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <button className="btn-primary" disabled={!canSubmit} onClick={submit}>
          {loading ? "Analyzing…" : "Analyze match"}
        </button>
        <button className="btn-ghost" onClick={loadSample} disabled={loading}>
          Load a sample
        </button>
        <span className="text-xs text-ink-faint">
          Nothing is stored except the anonymised result (name &amp; email are not persisted).
        </span>
      </div>
    </div>
  );
}

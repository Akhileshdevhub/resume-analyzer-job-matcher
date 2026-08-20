import { useState } from "react";
import { analyzePdf, analyzeText } from "./api";
import AnalyzeForm from "./components/AnalyzeForm";
import Dashboard from "./components/Dashboard";
import Header from "./components/Header";
import type { AnalysisResult } from "./types";

const STEPS = [
  { n: 1, t: "Upload or paste", d: "Add your resume (PDF) and the job description." },
  { n: 2, t: "We analyse", d: "Skills are extracted, normalised, and matched." },
  { n: 3, t: "See the breakdown", d: "An explainable score, gaps, and next steps." },
];

export default function App() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run(fn: () => Promise<AnalysisResult>) {
    setLoading(true);
    setError(null);
    try {
      setResult(await fn());
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6 sm:py-12">
        {result ? (
          <Dashboard result={result} onReset={() => setResult(null)} />
        ) : (
          <>
            <section className="mb-8 max-w-2xl">
              <h1 className="text-3xl font-bold tracking-tight text-ink sm:text-4xl">
                See how your resume matches a job — and why.
              </h1>
              <p className="mt-3 text-base leading-relaxed text-ink-muted">
                An explainable match score built from skill coverage and semantic
                similarity — not an opaque number from a language model. You get the
                matched skills, the gaps, project ideas to close them, and likely
                interview questions.
              </p>
              <div className="mt-6 grid gap-3 sm:grid-cols-3">
                {STEPS.map((s) => (
                  <div key={s.n} className="rounded-lg border border-slate-200 bg-white p-3">
                    <div className="flex h-6 w-6 items-center justify-center rounded-full bg-accent-soft text-xs font-bold text-accent">
                      {s.n}
                    </div>
                    <div className="mt-2 text-sm font-semibold text-ink">{s.t}</div>
                    <div className="mt-0.5 text-xs text-ink-muted">{s.d}</div>
                  </div>
                ))}
              </div>
            </section>

            <AnalyzeForm
              loading={loading}
              error={error}
              onSubmitPdf={(file, jd) => run(() => analyzePdf(file, jd))}
              onSubmitText={(resume, jd) => run(() => analyzeText(resume, jd))}
            />
          </>
        )}
      </main>

      <footer className="border-t border-slate-200 py-6 text-center text-xs text-ink-faint">
        Built with FastAPI, React &amp; scikit-learn · Explainable NLP scoring
      </footer>
    </div>
  );
}

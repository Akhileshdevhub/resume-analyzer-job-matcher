export default function Header() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4 sm:px-6">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-sm font-bold text-white">
            R
          </div>
          <span className="text-sm font-semibold text-ink">Resume Matcher</span>
        </div>
        <a
          href="https://github.com/"
          className="text-sm font-medium text-ink-muted hover:text-ink"
          target="_blank"
          rel="noreferrer"
        >
          GitHub
        </a>
      </div>
    </header>
  );
}

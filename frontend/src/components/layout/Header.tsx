interface HeaderProps {
  timestamp?: string;
  cacheHit?: boolean;
}

export function Header({ timestamp, cacheHit }: HeaderProps) {
  return (
    <header className="border-b border-rule">
      <div className="max-w-6xl mx-auto px-8 py-5 flex items-baseline justify-between">
        <div className="flex items-baseline gap-4">
          <span className="font-display text-xl font-medium tracking-tightest text-ink">
            GrineOS
          </span>
          <span className="hidden md:block w-px h-3 bg-rule-strong" />
          <span className="hidden md:block text-micro text-ink-secondary tracking-tight">
            The Operating System for Capital Allocation
          </span>
        </div>

        <div className="flex items-center gap-6">
          {timestamp && (
            <div className="flex items-center gap-2 text-micro text-ink-muted">
              <span className={`w-1.5 h-1.5 rounded-full ${cacheHit ? 'bg-ink-faint' : 'bg-regime-expansion'} animate-pulse`} />
              <span className="tabular font-mono">{timestamp}</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

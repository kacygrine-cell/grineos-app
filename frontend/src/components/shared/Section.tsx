import type { ReactNode } from 'react';
import clsx from 'clsx';

interface SectionProps {
  eyebrow: string;
  number?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}

/**
 * Document-style section — thin rule, small uppercase eyebrow, generous space.
 * The numbered eyebrow reinforces the editorial/memo feel.
 */
export function Section({
  eyebrow,
  number,
  action,
  children,
  className,
}: SectionProps) {
  return (
    <section className={clsx('section', className)}>
      <header className="flex items-baseline justify-between gap-6 mb-8">
        <div className="flex items-baseline gap-4">
          {number && (
            <span className="font-mono text-label text-ink-faint tabular">
              {number}
            </span>
          )}
          <h2 className="label">{eyebrow}</h2>
        </div>
        {action && <div className="text-micro text-ink-muted">{action}</div>}
      </header>
      <div>{children}</div>
    </section>
  );
}

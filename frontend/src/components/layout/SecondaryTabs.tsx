import { useState } from 'react';
import clsx from 'clsx';

type Tab = 'history' | 'analytics' | 'optimizer' | 'scenarios';

const tabs: { id: Tab; label: string }[] = [
  { id: 'history', label: 'Allocation History' },
  { id: 'analytics', label: 'Analytics' },
  { id: 'optimizer', label: 'Optimizer' },
  { id: 'scenarios', label: 'Scenarios' },
];

/**
 * Secondary surfaces. Everything here is a tool, not the product.
 * Deliberately understated: small type, thin underline, no fills.
 */
export function SecondaryTabs() {
  const [active, setActive] = useState<Tab>('history');

  return (
    <section className="section">
      <div className="flex items-center gap-1 mb-8 border-b border-rule">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setActive(t.id)}
            className={clsx(
              'px-4 py-3 text-micro uppercase tracking-wider font-medium transition-colors relative',
              active === t.id
                ? 'text-ink'
                : 'text-ink-muted hover:text-ink-secondary',
            )}
          >
            {t.label}
            {active === t.id && (
              <span className="absolute bottom-0 left-0 right-0 h-px bg-ink" />
            )}
          </button>
        ))}
      </div>

      <div className="min-h-[120px]">
        {active === 'history' && <HistoryPlaceholder />}
        {active === 'analytics' && <AnalyticsPlaceholder />}
        {active === 'optimizer' && <OptimizerPlaceholder />}
        {active === 'scenarios' && <ScenariosPlaceholder />}
      </div>
    </section>
  );
}

function HistoryPlaceholder() {
  return (
    <div className="text-sm text-ink-secondary max-w-xl">
      <p>
        Historical regime transitions and allocation changes. Review past
        rebalances and the signals that drove each one.
      </p>
    </div>
  );
}

function AnalyticsPlaceholder() {
  return (
    <div className="text-sm text-ink-secondary max-w-xl">
      <p>
        Supplementary analytics — volatility, correlations, factor exposures.
        These inform the regime engine; they are not the decision.
      </p>
    </div>
  );
}

function OptimizerPlaceholder() {
  return (
    <div className="text-sm text-ink-secondary max-w-xl">
      <p>
        Optimizer configuration. The Grine allocation engine applies
        constrained optimization within regime bands. Adjust the objective
        or covariance model here if needed.
      </p>
    </div>
  );
}

function ScenariosPlaceholder() {
  return (
    <div className="text-sm text-ink-secondary max-w-xl">
      <p>
        Stress test the current allocation across regime paths. Understand
        how the doctrine responds to transitions.
      </p>
    </div>
  );
}

import type { RegimeProbabilities } from '../../types';
import { pct } from '../../utils/format';

interface RegimeProbabilityBarProps {
  probabilities: RegimeProbabilities;
}

/**
 * Horizontal probability strip — three-segment bar with subtle labels.
 * Deliberately NOT a pie chart. Allocators scan left-to-right; they
 * want relative weights, not circular proportions.
 */
export function RegimeProbabilityBar({
  probabilities,
}: RegimeProbabilityBarProps) {
  const rows = [
    { label: 'Bull', value: probabilities.bull, tone: 'bg-regime-expansion' },
    { label: 'Bear', value: probabilities.bear, tone: 'bg-regime-endurance' },
    { label: 'Crisis', value: probabilities.crisis, tone: 'bg-regime-protection' },
  ];

  return (
    <div className="space-y-3 max-w-md">
      {rows.map((row) => (
        <div key={row.label} className="flex items-center gap-4">
          <div className="w-14 text-micro uppercase tracking-wider text-ink-muted font-medium">
            {row.label}
          </div>
          <div className="flex-1 h-[6px] bg-paper-sunken rounded-sm overflow-hidden">
            <div
              className={`h-full ${row.tone} transition-all duration-500`}
              style={{ width: `${row.value * 100}%` }}
            />
          </div>
          <div className="w-12 text-right tabular font-mono text-sm text-ink">
            {pct(row.value, 0)}
          </div>
        </div>
      ))}
    </div>
  );
}

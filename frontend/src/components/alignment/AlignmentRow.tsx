import clsx from 'clsx';
import type { RangeStatus } from '../../types';
import { pct, signed } from '../../utils/format';

interface AlignmentRowProps {
  label: string;
  userWeight: number;
  targetWeight: number;
  range: [number, number];
  deviation: number;
  status: RangeStatus;
}

const statusConfig: Record<
  RangeStatus,
  { label: string; tone: string; dot: string }
> = {
  inside: {
    label: 'Inside Range',
    tone: 'text-aligned',
    dot: 'bg-aligned',
  },
  above: {
    label: 'Above Range',
    tone: 'text-over',
    dot: 'bg-over',
  },
  below: {
    label: 'Below Range',
    tone: 'text-under',
    dot: 'bg-under',
  },
};

/**
 * Per-sleeve comparison row.
 *
 *   Equity   Current 58.0%    Doctrine 40.0% (35–45%)     Above +18.0%
 */
export function AlignmentRow({
  label,
  userWeight,
  targetWeight,
  range,
  deviation,
  status,
}: AlignmentRowProps) {
  const cfg = statusConfig[status];

  return (
    <div className="grid grid-cols-[72px_1fr_1fr_120px] gap-4 items-center py-4 border-b border-rule last:border-b-0">
      <div className="label">{label}</div>

      <div>
        <div className="text-micro text-ink-faint uppercase tracking-wider mb-1">
          Current
        </div>
        <div className="font-mono tabular text-lg text-ink">
          {pct(userWeight, 1)}
        </div>
      </div>

      <div>
        <div className="text-micro text-ink-faint uppercase tracking-wider mb-1">
          Doctrine
        </div>
        <div className="font-mono tabular text-lg text-ink-secondary">
          {pct(targetWeight, 1)}
          <span className="ml-2 text-micro text-ink-faint">
            ({pct(range[0], 0)}–{pct(range[1], 0)})
          </span>
        </div>
      </div>

      <div className="text-right">
        <div className="flex items-center justify-end gap-2 mb-1">
          <span className={clsx('w-1.5 h-1.5 rounded-full', cfg.dot)} />
          <span
            className={clsx(
              'text-micro font-medium uppercase tracking-wider',
              cfg.tone,
            )}
          >
            {cfg.label}
          </span>
        </div>
        <div className="font-mono tabular text-micro text-ink-muted">
          {signed(deviation, 1)}%
        </div>
      </div>
    </div>
  );
}

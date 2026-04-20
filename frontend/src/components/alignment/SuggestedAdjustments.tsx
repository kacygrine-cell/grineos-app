import clsx from 'clsx';

interface SuggestedAdjustmentsProps {
  adjustments: string[];
}

/**
 * Plain imperative actions. Each line is one move.
 * No fills, no icons — just verbs and numbers.
 */
export function SuggestedAdjustments({ adjustments }: SuggestedAdjustmentsProps) {
  if (adjustments.length === 0) {
    return (
      <div className="text-sm text-ink-muted italic font-display">
        No adjustments required. Portfolio is aligned with doctrine.
      </div>
    );
  }

  return (
    <ul className="space-y-2.5">
      {adjustments.map((action, i) => {
        const isReduce = action.startsWith('Reduce');
        return (
          <li
            key={i}
            className="flex items-baseline gap-3 text-sm text-ink leading-snug"
          >
            <span
              className={clsx(
                'font-mono text-micro tabular text-ink-faint mt-px',
              )}
            >
              {String(i + 1).padStart(2, '0')}
            </span>
            <span
              className={clsx(
                'inline-block w-2 h-px mt-2 flex-shrink-0',
                isReduce ? 'bg-over' : 'bg-regime-expansion',
              )}
            />
            <span>{action}</span>
          </li>
        );
      })}
    </ul>
  );
}

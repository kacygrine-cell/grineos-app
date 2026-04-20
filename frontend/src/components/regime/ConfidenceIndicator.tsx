import clsx from 'clsx';
import { confidenceLevel } from '../../utils/format';

interface ConfidenceIndicatorProps {
  confidence: number;
  size?: 'sm' | 'md' | 'lg';
}

/**
 * Three-step tick marker + label. No gauge, no dial — allocators read
 * confidence as a categorical signal, not a continuous one.
 */
export function ConfidenceIndicator({
  confidence,
  size = 'md',
}: ConfidenceIndicatorProps) {
  const level = confidenceLevel(confidence);
  const activeIndex = level === 'low' ? 0 : level === 'moderate' ? 1 : 2;

  const label = {
    low: 'Low',
    moderate: 'Moderate',
    high: 'High',
  }[level];

  const textSize = {
    sm: 'text-micro',
    md: 'text-sm',
    lg: 'text-base',
  }[size];

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-[3px]">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className={clsx(
              'h-[3px] transition-colors',
              i <= activeIndex ? 'bg-ink' : 'bg-rule',
              {
                'w-4': size === 'sm',
                'w-5': size === 'md',
                'w-7': size === 'lg',
              },
            )}
          />
        ))}
      </div>
      <span
        className={clsx(
          textSize,
          'tabular font-medium text-ink tracking-tight',
        )}
      >
        {label} Confidence
      </span>
      <span
        className={clsx('text-micro text-ink-faint tabular font-mono')}
      >
        {confidence.toFixed(2)}
      </span>
    </div>
  );
}

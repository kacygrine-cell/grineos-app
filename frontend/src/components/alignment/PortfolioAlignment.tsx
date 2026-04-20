import clsx from 'clsx';
import type { AlignmentResponse, AlignmentLabel } from '../../types';
import { AlignmentRow } from './AlignmentRow';
import { SuggestedAdjustments } from './SuggestedAdjustments';
import { regimeColorClass } from '../../utils/format';

interface PortfolioAlignmentProps {
  data: AlignmentResponse;
}

/**
 * Answers one question: "How aligned is this portfolio with the current
 * Grine allocation framework?"
 *
 * UI elements (all 8 required):
 *   1. Alignment Score (prominent)
 *   2. Alignment Label
 *   3. Current Regime context
 *   4. User portfolio weights      ┐
 *   5. Grine recommended target    │  all in rows
 *   6. Grine allocation ranges     │
 *   7. Deviations by sleeve        ┘
 *   8. Suggested adjustments
 */
export function PortfolioAlignment({ data }: PortfolioAlignmentProps) {
  const { regime, portfolio, recommended, alignment, suggested_adjustments } =
    data;

  return (
    <div className="space-y-10">
      {/* Header: score + label + regime context */}
      <AlignmentHeader
        score={alignment.score}
        label={alignment.label}
        regimeState={regime.state}
        confidence={regime.confidence}
      />

      {/* Per-sleeve comparison rows */}
      <div>
        <div className="label mb-3">Sleeve Comparison</div>
        <div>
          <AlignmentRow
            label="Equity"
            userWeight={portfolio.equity}
            targetWeight={recommended.target.equity}
            range={recommended.ranges.equity}
            deviation={alignment.deviations.equity}
            status={alignment.range_status.equity}
          />
          <AlignmentRow
            label="Bonds"
            userWeight={portfolio.bonds}
            targetWeight={recommended.target.bonds}
            range={recommended.ranges.bonds}
            deviation={alignment.deviations.bonds}
            status={alignment.range_status.bonds}
          />
          <AlignmentRow
            label="Cash"
            userWeight={portfolio.cash}
            targetWeight={recommended.target.cash}
            range={recommended.ranges.cash}
            deviation={alignment.deviations.cash}
            status={alignment.range_status.cash}
          />
        </div>
      </div>

      {/* Suggested adjustments */}
      <div className="pt-4 border-t border-rule">
        <div className="label mb-4">Suggested Adjustments</div>
        <SuggestedAdjustments adjustments={suggested_adjustments} />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------

interface AlignmentHeaderProps {
  score: number;
  label: AlignmentLabel;
  regimeState: string;
  confidence: string;
}

function AlignmentHeader({
  score,
  label,
  regimeState,
  confidence,
}: AlignmentHeaderProps) {
  return (
    <div className="grid grid-cols-[auto_1fr] gap-10 items-end">
      {/* Big score */}
      <div>
        <div className="label mb-3">Alignment Score</div>
        <div className="flex items-baseline gap-3">
          <span className="font-display text-7xl font-medium text-ink tabular leading-none">
            {score}
          </span>
          <span className="font-mono text-sm text-ink-faint tabular">
            / 100
          </span>
        </div>
        <div className="mt-4">
          <AlignmentBadge label={label} />
        </div>
      </div>

      {/* Regime context */}
      <div className="pb-2">
        <div className="label mb-3">Against Current Regime</div>
        <div className="flex items-baseline gap-3">
          <span
            className={clsx(
              'font-display text-3xl font-medium leading-none tracking-tightest',
              regimeColorClass(regimeState as any),
            )}
          >
            {regimeState}
          </span>
        </div>
        <div className="mt-2 text-micro text-ink-muted uppercase tracking-wider">
          {confidence.charAt(0) + confidence.slice(1).toLowerCase()} confidence
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------

function AlignmentBadge({ label }: { label: AlignmentLabel }) {
  const cfg: Record<
    AlignmentLabel,
    { tone: string }
  > = {
    'Highly Aligned': {
      tone: 'text-aligned border-aligned/50',
    },
    'Moderately Aligned': {
      tone: 'text-over border-over/50',
    },
    Misaligned: {
      tone: 'text-regime-endurance border-regime-endurance/50',
    },
  };
  const { tone } = cfg[label];
  return (
    <span
      className={clsx(
        'inline-block px-3 py-1.5 rounded-sm border text-micro uppercase tracking-wider font-medium',
        tone,
      )}
    >
      {label}
    </span>
  );
}

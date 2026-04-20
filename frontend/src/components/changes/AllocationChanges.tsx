import clsx from 'clsx';
import type {
  AllocationResponse,
  RegimeResponse,
  ChangeMagnitude,
} from '../../types';
import { momentumLabel, pct, signed } from '../../utils/format';

interface AllocationChangesProps {
  allocation: AllocationResponse;
  regime: RegimeResponse;
  previousAllocation?: AllocationResponse | null;
}

/**
 * "Why it changed" — short, structured signals behind the allocation move.
 * Surfaces: regime, confidence, momentum, turnover constraint, deltas.
 * Deliberately sparse — the narrative is what matters, not the data dump.
 */
export function AllocationChanges({
  allocation,
  regime,
  previousAllocation,
}: AllocationChangesProps) {
  const magnitude = allocation.change_magnitude ?? 'minor';

  const signals = buildSignals(allocation, regime, previousAllocation);

  return (
    <div className="grid grid-cols-12 gap-10 items-start">
      {/* Headline reason */}
      <div className="col-span-12 lg:col-span-5">
        <div className="flex items-center gap-3 mb-4">
          <MagnitudeBadge magnitude={magnitude} />
        </div>

        <p className="font-display text-xl leading-snug text-ink">
          {allocation.change_reason ??
            'Allocation updated based on current regime signals.'}
        </p>
      </div>

      {/* Structured signals */}
      <div className="col-span-12 lg:col-span-7">
        <div className="label mb-4">Driving Signals</div>
        <dl className="divide-y divide-rule">
          {signals.map((s) => (
            <div
              key={s.key}
              className="grid grid-cols-[140px_1fr_auto] gap-6 items-baseline py-3"
            >
              <dt className="label">{s.label}</dt>
              <dd className="text-sm text-ink-secondary">{s.description}</dd>
              <dd className="font-mono tabular text-sm text-ink">{s.value}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  );
}

function MagnitudeBadge({ magnitude }: { magnitude: ChangeMagnitude }) {
  const cfg = {
    initial: { label: 'Initial', tone: 'text-ink-muted border-ink-faint/50' },
    minor: { label: 'Minor Change', tone: 'text-under border-under/50' },
    moderate: { label: 'Moderate Change', tone: 'text-over border-over/50' },
    major: { label: 'Major Change', tone: 'text-regime-endurance border-regime-endurance/50' },
  }[magnitude];

  return (
    <span
      className={clsx(
        'px-2.5 py-1 rounded-sm border text-micro uppercase tracking-wider font-medium',
        cfg.tone,
      )}
    >
      {cfg.label}
    </span>
  );
}

interface Signal {
  key: string;
  label: string;
  description: string;
  value: string;
}

function buildSignals(
  allocation: AllocationResponse,
  regime: RegimeResponse,
  previous?: AllocationResponse | null,
): Signal[] {
  const signals: Signal[] = [];

  // Regime
  signals.push({
    key: 'regime',
    label: 'Regime',
    description: previous
      ? previous.constraints.regime_state !==
        allocation.constraints.regime_state
        ? `Shifted from ${previous.constraints.regime_state} to ${allocation.constraints.regime_state}.`
        : `Remains ${allocation.constraints.regime_state}.`
      : `Classified as ${allocation.constraints.regime_state}.`,
    value: allocation.constraints.regime_state,
  });

  // Confidence
  signals.push({
    key: 'confidence',
    label: 'Confidence',
    description:
      regime.confidence >= 0.7
        ? 'Regime signal is strong; doctrine bands applied with conviction.'
        : regime.confidence >= 0.4
        ? 'Moderate signal; positioning held near band midpoints.'
        : 'Weak signal; weights pulled toward conservative defaults.',
    value: regime.confidence.toFixed(2),
  });

  // Momentum
  signals.push({
    key: 'momentum',
    label: 'Momentum',
    description: `${momentumLabel(regime.momentum)}. ${
      regime.momentum > 0.1
        ? 'Tilts equity toward upper band.'
        : regime.momentum < -0.1
        ? 'Tilts toward defensive edge of band.'
        : 'Neutral tilt; target near band center.'
    }`,
    value: signed(regime.momentum, 2),
  });

  // Turnover
  signals.push({
    key: 'turnover',
    label: 'Turnover',
    description: allocation.turnover.capped
      ? `Move exceeded the ${pct(allocation.turnover.cap, 0)} cap; partial rebalance executed.`
      : `Move within the ${pct(allocation.turnover.cap, 0)} cap; full target applied.`,
    value: pct(allocation.turnover.realized, 1),
  });

  // Equity delta vs previous (if available)
  if (previous) {
    const dEq =
      allocation.final_weights.equity - previous.final_weights.equity;
    signals.push({
      key: 'equity-delta',
      label: 'Equity Change',
      description:
        Math.abs(dEq) < 0.005
          ? 'Equity weight essentially unchanged.'
          : dEq > 0
          ? 'Equity increased.'
          : 'Equity reduced.',
      value: signed(dEq, 1),
    });
  }

  return signals;
}

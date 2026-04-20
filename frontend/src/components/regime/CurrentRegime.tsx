import type { RegimeResponse } from '../../types';
import {
  momentumLabel,
  momentumDirection,
  regimeNarrative,
  regimeColorClass,
} from '../../utils/format';
import { ConfidenceIndicator } from './ConfidenceIndicator';
import { RegimeProbabilityBar } from './RegimeProbabilityBar';

interface CurrentRegimeProps {
  data: RegimeResponse;
}

/**
 * The regime state is the primary message of GrineOS. Typography-first,
 * no card chrome, generous whitespace. This is the first thing an
 * allocator reads and should instantly convey: "Where are we?"
 */
export function CurrentRegime({ data }: CurrentRegimeProps) {
  const stateColor = regimeColorClass(data.final_state);
  const momDir = momentumDirection(data.momentum);

  return (
    <div className="grid grid-cols-12 gap-8 items-start">
      {/* Left: state name — dominant */}
      <div className="col-span-12 lg:col-span-7">
        <div className="label mb-4">Market Regime</div>

        <h1
          className={`regime-state-display text-[clamp(3.5rem,9vw,7.5rem)] leading-[0.95] ${stateColor}`}
        >
          {data.final_state}
        </h1>

        <p className="mt-6 font-display text-lg text-ink-secondary max-w-xl leading-snug">
          {regimeNarrative(data.final_state)}
        </p>
      </div>

      {/* Right: supporting data */}
      <div className="col-span-12 lg:col-span-5 lg:pt-4 space-y-8">
        <div>
          <div className="label mb-3">Confidence</div>
          <ConfidenceIndicator confidence={data.confidence} size="md" />
        </div>

        <div>
          <div className="label mb-3">Momentum</div>
          <div className="flex items-baseline gap-3">
            <MomentumGlyph direction={momDir} />
            <span className="font-medium text-ink tabular">
              {momentumLabel(data.momentum)}
            </span>
            <span className="font-mono text-micro text-ink-faint tabular">
              {data.momentum > 0 ? '+' : ''}
              {data.momentum.toFixed(2)}
            </span>
          </div>
        </div>

        {data.probabilities && (
          <div>
            <div className="label mb-3">Regime Probabilities</div>
            <RegimeProbabilityBar probabilities={data.probabilities} />
          </div>
        )}
      </div>
    </div>
  );
}

function MomentumGlyph({ direction }: { direction: 'up' | 'down' | 'flat' }) {
  if (direction === 'up') {
    return (
      <svg width="18" height="10" viewBox="0 0 18 10" className="text-regime-expansion">
        <path d="M1 8L9 2L17 8" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  }
  if (direction === 'down') {
    return (
      <svg width="18" height="10" viewBox="0 0 18 10" className="text-regime-endurance">
        <path d="M1 2L9 8L17 2" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  }
  return (
    <svg width="18" height="10" viewBox="0 0 18 10" className="text-ink-muted">
      <path d="M1 5L17 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

import type { DividendSplit as DividendSplitType } from '../../types';
import { pct } from '../../utils/format';

interface DividendSplitProps {
  split: DividendSplitType;
}

export function DividendSplit({ split }: DividendSplitProps) {
  if (split.equity_total <= 0) return null;

  const growthShare = 1 - split.dividend_share;

  return (
    <div className="pt-8 border-t border-rule">
      <div className="flex items-baseline justify-between mb-3">
        <div className="label">Equity Composition</div>
        <div className="text-micro text-ink-faint tabular font-mono">
          Regime band: {pct(split.range_lower, 0)} – {pct(split.range_upper, 0)}
        </div>
      </div>

      {/* Two-segment bar */}
      <div className="flex h-[8px] rounded-sm overflow-hidden bg-paper-sunken">
        <div
          className="bg-bronze-light"
          style={{ width: `${growthShare * 100}%` }}
        />
        <div
          className="bg-bronze-dark"
          style={{ width: `${split.dividend_share * 100}%` }}
        />
      </div>

      <div className="mt-3 flex items-baseline justify-between text-sm">
        <div className="flex items-baseline gap-2">
          <span className="w-2 h-2 rounded-full bg-bronze-light inline-block" />
          <span className="text-ink-secondary">Growth</span>
          <span className="font-mono tabular text-ink">
            {pct(split.growth, 1)}
          </span>
          <span className="text-ink-faint font-mono tabular text-micro">
            ({pct(growthShare, 0)} of equity)
          </span>
        </div>

        <div className="flex items-baseline gap-2">
          <span className="w-2 h-2 rounded-full bg-bronze-dark inline-block" />
          <span className="text-ink-secondary">Dividend</span>
          <span className="font-mono tabular text-ink">
            {pct(split.dividend, 1)}
          </span>
          <span className="text-ink-faint font-mono tabular text-micro">
            ({pct(split.dividend_share, 0)} of equity)
          </span>
        </div>
      </div>
    </div>
  );
}

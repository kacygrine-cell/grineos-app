import type { AllocationResponse } from '../../types';
import { AllocationBand, AllocationBandLegend } from './AllocationBand';
import { DividendSplit } from './DividendSplit';

interface RecommendedAllocationProps {
  data: AllocationResponse;
}

export function RecommendedAllocation({ data }: RecommendedAllocationProps) {
  const { final_weights, target_weights, constraints, dividend_split } = data;

  // Unified x-axis: show each row on a 0-80% scale so bands are comparable.
  // Equity can reach 70% max; 80% gives visual headroom.
  const scale = 0.8;

  return (
    <div className="space-y-8">
      {/* Asset rows */}
      <div className="space-y-7">
        <AllocationBand
          label="Equity"
          weight={final_weights.equity}
          target={target_weights.equity}
          range={constraints.ranges.equity}
          color="#6B8E4E"
          max={scale}
        />
        <AllocationBand
          label="Bonds"
          weight={final_weights.bonds}
          target={target_weights.bonds}
          range={constraints.ranges.bonds}
          color="#5A564E"
          max={scale}
        />
        <AllocationBand
          label="Cash"
          weight={final_weights.cash}
          target={target_weights.cash}
          range={constraints.ranges.cash}
          color="#7A5B3F"
          max={scale}
        />
      </div>

      {/* Legend */}
      <div className="flex items-center justify-between pt-4 border-t border-rule">
        <AllocationBandLegend />
        <div className="text-micro text-ink-muted tabular font-mono">
          Turnover: {(data.turnover.realized * 100).toFixed(1)}%
          {data.turnover.capped && (
            <span className="ml-2 text-bronze">· capped</span>
          )}
        </div>
      </div>

      {/* Dividend composition */}
      <DividendSplit split={dividend_split} />
    </div>
  );
}

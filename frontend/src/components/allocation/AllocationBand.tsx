import clsx from 'clsx';
import type { Range } from '../../types';
import { pct } from '../../utils/format';

interface AllocationBandProps {
  label: string;
  weight: number;
  target: number;
  range: Range;
  color: string;
  max?: number; // normalize to a shared scale across rows; default 1
}

/**
 * A single asset row: label, weight, band [lower, upper] with a tick.
 * The band is the doctrine; the weight is where we sit within it.
 * Shown on a shared 0–100% scale so rows are directly comparable.
 */
export function AllocationBand({
  label,
  weight,
  target,
  range,
  color,
  max = 1,
}: AllocationBandProps) {
  const scale = (v: number) => (v / max) * 100;

  return (
    <div className="grid grid-cols-[90px_1fr_90px] gap-6 items-center">
      {/* Label */}
      <div className="label">{label}</div>

      {/* Track with band and weight marker */}
      <div className="relative h-8">
        {/* Background scale line */}
        <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 h-px bg-rule" />

        {/* Constraint band */}
        <div
          className="absolute top-1/2 -translate-y-1/2 h-[6px] rounded-sm"
          style={{
            left: `${scale(range.lower)}%`,
            width: `${scale(range.upper - range.lower)}%`,
            backgroundColor: color,
            opacity: 0.18,
          }}
        />

        {/* Band edges */}
        <div
          className="absolute top-1/2 -translate-y-1/2 w-px h-[10px]"
          style={{ left: `${scale(range.lower)}%`, backgroundColor: color, opacity: 0.5 }}
        />
        <div
          className="absolute top-1/2 -translate-y-1/2 w-px h-[10px]"
          style={{ left: `${scale(range.upper)}%`, backgroundColor: color, opacity: 0.5 }}
        />

        {/* Target marker (pre-turnover) — light dashed tick */}
        <div
          className="absolute top-1/2 -translate-y-1/2 w-px h-[18px] border-l border-dashed opacity-40"
          style={{ left: `${scale(target)}%`, borderColor: color }}
        />

        {/* Weight tick — solid, dominant */}
        <div
          className="absolute top-1/2 -translate-y-1/2 w-[2px] h-[22px]"
          style={{ left: `${scale(weight)}%`, backgroundColor: color }}
        />

        {/* Range labels */}
        <div
          className="absolute -bottom-[2px] font-mono text-[10px] text-ink-faint tabular -translate-x-1/2"
          style={{ left: `${scale(range.lower)}%` }}
        >
          {pct(range.lower, 0)}
        </div>
        <div
          className="absolute -bottom-[2px] font-mono text-[10px] text-ink-faint tabular -translate-x-1/2"
          style={{ left: `${scale(range.upper)}%` }}
        >
          {pct(range.upper, 0)}
        </div>
      </div>

      {/* Weight value */}
      <div className="text-right">
        <div className="font-display text-2xl font-medium text-ink tabular leading-none">
          {pct(weight, 1)}
        </div>
      </div>
    </div>
  );
}

export function AllocationBandLegend() {
  return (
    <div className="flex items-center gap-5 text-micro text-ink-muted">
      <div className="flex items-center gap-2">
        <span className="block w-3 h-[6px] bg-ink rounded-sm opacity-20" />
        <span>Band</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="block w-px h-3 border-l border-dashed border-ink-muted" />
        <span>Target</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="block w-[2px] h-3 bg-ink" />
        <span>Recommended</span>
      </div>
    </div>
  );
}

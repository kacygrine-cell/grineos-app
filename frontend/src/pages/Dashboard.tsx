import { useMemo } from 'react';
import { Header } from '../components/layout/Header';
import { SecondaryTabs } from '../components/layout/SecondaryTabs';
import { Section } from '../components/shared/Section';
import { CurrentRegime } from '../components/regime/CurrentRegime';
import { RecommendedAllocation } from '../components/allocation/RecommendedAllocation';
import { PortfolioAlignment } from '../components/alignment/PortfolioAlignment';
import { AllocationChanges } from '../components/changes/AllocationChanges';
import {
  useRegime,
  useAllocation,
  useAllocationHistory,
  useAlignment,
} from '../hooks';
import { formatTimestamp } from '../utils/format';
import type { AllocationWeights } from '../types';

/**
 * Dashboard composition — the allocation decision surface.
 *
 *   ①  Current Regime           (full-width, dominant)
 *   ②  Recommended Allocation   + ③ Portfolio Alignment  (two columns)
 *   ④  Why It Changed           (full-width, structured)
 *      ─
 *      Secondary: history / analytics / optimizer / scenarios
 */
export function Dashboard() {
  const regimeQ = useRegime();
  const allocQ = useAllocation();
  const historyQ = useAllocationHistory(30, 10);

  // TEMPORARY: user portfolio is mocked until the portfolio-ingest endpoint
  // ships. When wired up, pull this from a usePortfolio() hook backed by
  // GET /portfolio/current.
  const userWeights: AllocationWeights = useMemo(
    () => ({ equity: 0.58, bonds: 0.32, cash: 0.10 }),
    [],
  );

  // Server-side alignment — POSTs to /portfolio/alignment
  const alignmentQ = useAlignment(userWeights);

  if (regimeQ.isLoading || allocQ.isLoading) {
    return <DashboardSkeleton />;
  }

  if (regimeQ.isError || !regimeQ.data) {
    return <ErrorState message="Unable to load current regime." />;
  }

  if (allocQ.isError || !allocQ.data) {
    return <ErrorState message="Unable to load allocation recommendation." />;
  }

  const regime = regimeQ.data;
  const allocation = allocQ.data;
  const alignment = alignmentQ.data ?? null;
  const previousAllocation = historyQ.data?.current ?? null;

  return (
    <div className="min-h-screen bg-paper text-ink">
      <Header
        timestamp={formatTimestamp(allocation.created_at)}
        cacheHit={regime.metadata.cache_hit}
      />

      <main className="max-w-6xl mx-auto px-8">
        {/* ① CURRENT REGIME — dominant */}
        <Section eyebrow="Current Regime" number="01">
          <CurrentRegime data={regime} />
        </Section>

        {/* ② RECOMMENDED ALLOCATION  +  ③ PORTFOLIO ALIGNMENT */}
        <div className="grid grid-cols-12 gap-10 border-t border-rule">
          <div className="col-span-12 lg:col-span-7 py-10 lg:border-r lg:border-rule lg:pr-10">
            <header className="flex items-baseline gap-4 mb-8">
              <span className="font-mono text-label text-ink-faint tabular">
                02
              </span>
              <h2 className="label">Recommended Allocation</h2>
            </header>
            <RecommendedAllocation data={allocation} />
          </div>

          <div className="col-span-12 lg:col-span-5 py-10">
            <header className="flex items-baseline gap-4 mb-8">
              <span className="font-mono text-label text-ink-faint tabular">
                03
              </span>
              <h2 className="label">Portfolio Alignment</h2>
            </header>
            {alignmentQ.isLoading ? (
              <AlignmentSkeleton />
            ) : alignment ? (
              <PortfolioAlignment data={alignment} />
            ) : (
              <EmptyPortfolio />
            )}
          </div>
        </div>

        {/* ④ WHY IT CHANGED */}
        <Section eyebrow="Why It Changed" number="04">
          <AllocationChanges
            allocation={allocation}
            regime={regime}
            previousAllocation={previousAllocation}
          />
        </Section>

        {/* Secondary surfaces — deliberately minor */}
        <SecondaryTabs />

        <footer className="py-12 text-micro text-ink-faint text-center tabular font-mono">
          GrineOS · Powered by grine_regime_engine v0.3.0
        </footer>
      </main>
    </div>
  );
}

// -----------------------------------------------------------------------------

function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-paper">
      <Header />
      <main className="max-w-6xl mx-auto px-8 py-20">
        <div className="animate-pulse space-y-12">
          <div className="h-40 bg-paper-sunken rounded-sm" />
          <div className="grid grid-cols-2 gap-10">
            <div className="h-60 bg-paper-sunken rounded-sm" />
            <div className="h-60 bg-paper-sunken rounded-sm" />
          </div>
          <div className="h-32 bg-paper-sunken rounded-sm" />
        </div>
      </main>
    </div>
  );
}

function AlignmentSkeleton() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="h-20 bg-paper-sunken rounded-sm" />
      <div className="h-40 bg-paper-sunken rounded-sm" />
    </div>
  );
}

function EmptyPortfolio() {
  return (
    <div className="py-8">
      <p className="font-display text-lg text-ink-secondary leading-snug max-w-sm">
        No portfolio on file. Submit your current holdings to see how they
        compare with the Grine doctrine.
      </p>
      <button className="mt-6 px-4 py-2 border border-ink-secondary text-micro uppercase tracking-wider text-ink font-medium hover:bg-ink-secondary hover:text-paper transition-colors">
        Input Portfolio
      </button>
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="min-h-screen bg-paper flex items-center justify-center">
      <div className="text-center max-w-md">
        <div className="label mb-3">Unable to Load</div>
        <p className="font-display text-xl text-ink-secondary">{message}</p>
      </div>
    </div>
  );
}

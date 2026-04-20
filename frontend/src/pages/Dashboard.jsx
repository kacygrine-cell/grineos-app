import React, { useMemo } from 'react';
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
  const userWeights = useMemo(
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
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
      color: 'white'
    }}>
      <Header
        timestamp={formatTimestamp(allocation.created_at)}
        cacheHit={regime.metadata?.cache_hit}
      />

      <main style={{
        maxWidth: '72rem',
        margin: '0 auto',
        padding: '0 2rem'
      }}>
        {/* ① CURRENT REGIME — dominant */}
        <Section title="Current Regime" subtitle="01">
          <CurrentRegime regimeQ={regimeQ} />
        </Section>

        {/* ② RECOMMENDED ALLOCATION  +  ③ PORTFOLIO ALIGNMENT */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(12, 1fr)',
          gap: '2.5rem',
          borderTop: '1px solid rgba(255,255,255,0.1)',
          marginTop: '2rem'
        }}>
          <div style={{
            gridColumn: 'span 7',
            padding: '2.5rem 0',
            borderRight: '1px solid rgba(255,255,255,0.1)',
            paddingRight: '2.5rem'
          }}>
            <header style={{
              display: 'flex',
              alignItems: 'baseline',
              gap: '1rem',
              marginBottom: '2rem'
            }}>
              <span style={{
                fontFamily: 'monospace',
                fontSize: '0.875rem',
                color: '#78909c'
              }}>
                02
              </span>
              <h2 style={{
                fontSize: '1.1rem',
                fontWeight: '600',
                color: 'white',
                margin: '0'
              }}>
                Recommended Allocation
              </h2>
            </header>
            <RecommendedAllocation allocQ={allocQ} />
          </div>

          <div style={{
            gridColumn: 'span 5',
            padding: '2.5rem 0'
          }}>
            <header style={{
              display: 'flex',
              alignItems: 'baseline',
              gap: '1rem',
              marginBottom: '2rem'
            }}>
              <span style={{
                fontFamily: 'monospace',
                fontSize: '0.875rem',
                color: '#78909c'
              }}>
                03
              </span>
              <h2 style={{
                fontSize: '1.1rem',
                fontWeight: '600',
                color: 'white',
                margin: '0'
              }}>
                Portfolio Alignment
              </h2>
            </header>
            {alignmentQ.isLoading ? (
              <AlignmentSkeleton />
            ) : alignment ? (
              <PortfolioAlignment />
            ) : (
              <EmptyPortfolio />
            )}
          </div>
        </div>

        {/* ④ WHY IT CHANGED */}
        <Section title="Why It Changed" subtitle="04">
          <AllocationChanges
            allocation={allocation}
            regime={regime}
            previousAllocation={previousAllocation}
            historyQ={historyQ}
          />
        </Section>

        {/* Secondary surfaces — deliberately minor */}
        <SecondaryTabs />

        <footer style={{
          padding: '3rem 0',
          fontSize: '0.75rem',
          color: '#78909c',
          textAlign: 'center',
          fontFamily: 'monospace'
        }}>
          GrineOS · Powered by grine_regime_engine v0.3.0
        </footer>
      </main>
    </div>
  );
}

// -----------------------------------------------------------------------------

function DashboardSkeleton() {
  return (
    <div style={{ minHeight: '100vh', background: '#1a1a2e' }}>
      <Header />
      <main style={{
        maxWidth: '72rem',
        margin: '0 auto',
        padding: '5rem 2rem'
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '3rem' }}>
          <div style={{
            height: '10rem',
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '6px',
            animation: 'pulse 2s infinite'
          }} />
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '2.5rem'
          }}>
            <div style={{
              height: '15rem',
              background: 'rgba(255,255,255,0.05)',
              borderRadius: '6px'
            }} />
            <div style={{
              height: '15rem',
              background: 'rgba(255,255,255,0.05)',
              borderRadius: '6px'
            }} />
          </div>
          <div style={{
            height: '8rem',
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '6px'
          }} />
        </div>
      </main>
    </div>
  );
}

function AlignmentSkeleton() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{
        height: '5rem',
        background: 'rgba(255,255,255,0.05)',
        borderRadius: '6px'
      }} />
      <div style={{
        height: '10rem',
        background: 'rgba(255,255,255,0.05)',
        borderRadius: '6px'
      }} />
    </div>
  );
}

function EmptyPortfolio() {
  return (
    <div style={{ padding: '2rem 0' }}>
      <p style={{
        fontSize: '1.125rem',
        color: '#b0bec5',
        lineHeight: '1.6',
        maxWidth: '24rem',
        marginBottom: '1.5rem'
      }}>
        No portfolio on file. Submit your current holdings to see how they
        compare with the Grine doctrine.
      </p>
      <button style={{
        padding: '0.5rem 1rem',
        border: '1px solid #b0bec5',
        background: 'transparent',
        color: 'white',
        fontSize: '0.75rem',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        fontWeight: '500',
        cursor: 'pointer',
        transition: 'all 0.2s ease'
      }}>
        Input Portfolio
      </button>
    </div>
  );
}

function ErrorState({ message }) {
  return (
    <div style={{
      minHeight: '100vh',
      background: '#1a1a2e',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div style={{
        textAlign: 'center',
        maxWidth: '28rem'
      }}>
        <div style={{
          fontSize: '1.1rem',
          fontWeight: '600',
          marginBottom: '0.75rem',
          color: 'white'
        }}>
          Unable to Load
        </div>
        <p style={{
          fontSize: '1.25rem',
          color: '#b0bec5'
        }}>
          {message}
        </p>
      </div>
    </div>
  );
}

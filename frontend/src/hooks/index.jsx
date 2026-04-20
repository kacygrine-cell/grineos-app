import { useState, useEffect } from 'react';

// Simplified hooks with immediate data loading for demo purposes
export function useRegime() {
  const [regimeData] = useState({
    data: {
      final_state: 'EXPANSION',
      confidence: 0.94,
      momentum: 0.85,
      metadata: {
        cache_hit: true,
        processing_time_ms: 120
      },
      detection_id: 'demo-regime-001',
      tenant_id: 'demo-tenant',
      created_at: new Date().toISOString()
    },
    isLoading: false,
    isError: false,
    error: null
  });

  return regimeData;
}

export function useAllocation() {
  const [allocationData] = useState({
    data: {
      final_weights: {
        equity: 0.75,
        bonds: 0.15,
        cash: 0.10
      },
      constraints: {
        regime_state: 'EXPANSION',
        ranges: {
          equity: { lower: 0.60, upper: 0.85 },
          bonds: { lower: 0.10, upper: 0.30 },
          cash: { lower: 0.05, upper: 0.15 }
        },
        turnover_cap: 0.20,
        objective: 'max_sharpe'
      },
      turnover: {
        realized: 0.12,
        proposed: 0.15,
        cap: 0.20,
        capped: false
      },
      dividend_split: {
        equity_total: 0.75,
        growth: 0.45,
        dividend: 0.30,
        dividend_share: 0.40,
        range_lower: 0.35,
        range_upper: 0.55
      },
      created_at: new Date().toISOString(),
      recommendation_id: 'demo-alloc-001'
    },
    isLoading: false,
    isError: false,
    error: null
  });

  return allocationData;
}

export function useAllocationHistory() {
  const [historyData] = useState({
    data: {
      current: {
        final_weights: { equity: 0.75, bonds: 0.15, cash: 0.10 },
        created_at: new Date().toISOString()
      },
      history: [
        {
          recommendation_id: 'demo-hist-001',
          weights: { equity: 0.70, bonds: 0.20, cash: 0.10 },
          regime_state: 'BALANCED',
          confidence: 0.89,
          momentum: 0.45,
          turnover: 0.08,
          change_magnitude: 'minor',
          created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
        }
      ],
      total_count: 1,
      date_range: { start: '2024-01-01', end: '2024-12-31' },
      stats: {
        avg_turnover: 0.08,
        regime_distribution: { EXPANSION: 0.6, BALANCED: 0.4 },
        rebalance_frequency: 12
      }
    },
    isLoading: false,
    isError: false,
    error: null
  });

  return historyData;
}

export function useAlignment() {
  const [alignmentData] = useState({
    data: {
      regime: {
        state: 'EXPANSION',
        confidence: 'HIGH',
        confidence_value: 0.94
      },
      portfolio: { equity: 0.58, bonds: 0.32, cash: 0.10 },
      recommended: {
        target: { equity: 0.75, bonds: 0.15, cash: 0.10 },
        ranges: {
          equity: [0.60, 0.85],
          bonds: [0.10, 0.30],
          cash: [0.05, 0.15]
        }
      },
      alignment: {
        score: 87,
        label: 'Moderately Aligned',
        deviations: {
          equity: -0.17,
          bonds: 0.17,
          cash: 0.00
        },
        range_status: {
          equity: 'below',
          bonds: 'above',
          cash: 'inside'
        },
        penalty_breakdown: {
          weight_deviation: 15,
          range_violation: 5
        }
      },
      suggested_adjustments: [
        'Increase equity allocation by 17%',
        'Reduce bond allocation by 17%',
        'Cash allocation is optimal'
      ],
      tenant_id: 'demo-tenant'
    },
    isLoading: false,
    isError: false,
    error: null
  });

  return alignmentData;
}

import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import type {
  AlignmentRequest,
  AllocationWeights,
} from '../types';

// --- Regime ----------------------------------------------------------------

export const useRegime = () =>
  useQuery({
    queryKey: ['regime', 'current'],
    queryFn: () => api.regime.current(),
    refetchInterval: 60_000,
    staleTime: 30_000,
  });

// --- Allocation ------------------------------------------------------------

export const useAllocation = (objective?: string) =>
  useQuery({
    queryKey: ['allocation', 'recommended', objective],
    queryFn: () => api.allocation.recommended({ objective }),
    refetchInterval: 60_000,
    staleTime: 30_000,
  });

export const useAllocationHistory = (days = 30, limit = 50) =>
  useQuery({
    queryKey: ['allocation', 'history', days, limit],
    queryFn: () => api.allocation.history(days, limit),
  });

// --- Portfolio Alignment (server-side) -------------------------------------

/**
 * Server-side alignment. Posts the user's portfolio to the backend, which
 * fetches the canonical regime + recommendation and returns a full verdict
 * including score, deviations, range status, and suggested adjustments.
 */
export const useAlignment = (weights: AllocationWeights | null) =>
  useQuery({
    queryKey: ['portfolio', 'alignment', weights],
    queryFn: () => {
      if (!weights) throw new Error('No portfolio weights');
      const body: AlignmentRequest = {
        equity: weights.equity,
        bonds: weights.bonds,
        cash: weights.cash,
      };
      return api.portfolio.alignment(body);
    },
    enabled: weights !== null,
    refetchInterval: 60_000,
    staleTime: 30_000,
  });

/**
 * Sample alignment for empty states — uses a default 60/30/10 portfolio.
 */
export const useAlignmentSample = () =>
  useQuery({
    queryKey: ['portfolio', 'alignment', 'sample'],
    queryFn: () => api.portfolio.alignmentSample(),
  });

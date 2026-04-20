import type {
  RegimeResponse,
  AllocationResponse,
  AllocationHistoryResponse,
  AlignmentRequest,
  AlignmentResponse,
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api/v1';
const TENANT_ID = import.meta.env.VITE_TENANT_ID ?? '';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      'X-Tenant-ID': TENANT_ID,
      ...(init?.headers ?? {}),
    },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new ApiError(res.status, text);
  }

  return res.json() as Promise<T>;
}

export const api = {
  regime: {
    current: (forceRefresh = false) =>
      request<RegimeResponse>(
        `/regime/current${forceRefresh ? '?force_refresh=true' : ''}`,
      ),
  },
  allocation: {
    recommended: (params?: {
      force_refresh?: boolean;
      objective?: string;
      turnover_cap?: number;
    }) => {
      const q = new URLSearchParams();
      if (params?.force_refresh) q.set('force_refresh', 'true');
      if (params?.objective) q.set('objective', params.objective);
      if (params?.turnover_cap != null)
        q.set('turnover_cap', String(params.turnover_cap));
      const query = q.toString();
      return request<AllocationResponse>(
        `/allocation/recommended${query ? `?${query}` : ''}`,
      );
    },
    history: (daysLookback = 30, limit = 50) =>
      request<AllocationHistoryResponse>(
        `/allocation/history?days_lookback=${daysLookback}&limit=${limit}`,
      ),
  },
  portfolio: {
    alignment: (body: AlignmentRequest) =>
      request<AlignmentResponse>('/portfolio/alignment', {
        method: 'POST',
        body: JSON.stringify(body),
      }),
    alignmentSample: () =>
      request<AlignmentResponse>('/portfolio/alignment/sample'),
  },
};

export { ApiError };

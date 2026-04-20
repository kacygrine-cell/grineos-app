const API_BASE = import.meta.env.VITE_API_BASE ?? '/api/v1';
const TENANT_ID = import.meta.env.VITE_TENANT_ID ?? '';

class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

async function request(path, init) {
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
  
  return res.json();
}

export const api = {
  regime: {
    current: (forceRefresh = false) =>
      request(
        `/regime/current${forceRefresh ? '?force_refresh=true' : ''}`,
      ),
  },

  allocation: {
    recommended: (params) => {
      const q = new URLSearchParams();
      if (params?.force_refresh) q.set('force_refresh', 'true');
      if (params?.objective) q.set('objective', params.objective);
      if (params?.turnover_cap != null)
        q.set('turnover_cap', String(params.turnover_cap));
      const query = q.toString();
      return request(
        `/allocation/recommended${query ? `?${query}` : ''}`,
      );
    },

    history: (daysLookback = 30, limit = 50) =>
      request(
        `/allocation/history?days_lookback=${daysLookback}&limit=${limit}`,
      ),
  },

  portfolio: {
    alignment: (body) =>
      request('/portfolio/alignment', {
        method: 'POST',
        body: JSON.stringify(body),
      }),

    alignmentSample: () =>
      request('/portfolio/alignment/sample'),
  },
};

export { ApiError };

# GrineOS — Architecture

*The operating system for capital allocation.*

This document declares the structural rules of the system. Every service,
endpoint, and component must obey these rules. If a change would violate
them, the change must be rethought.

---

## 1. Dependency Graph

```
                         ┌──────────────────────────────┐
                         │     grine_regime_engine       │
                         │   (installable Python pkg)    │
                         │                               │
                         │   • RegimeEngine              │
                         │   • run_allocation() (v2)     │
                         │   • REGIME_RANGES             │
                         └───────────────┬───────────────┘
                                         │
          ┌──────────────────────────────┼──────────────────────────────┐
          │                              │                              │
          ▼                              ▼                              ▼
   ┌─────────────┐             ┌──────────────────┐         ┌────────────────────┐
   │ RegimeSvc   │ ◀────────── │ AllocationSvc    │ ◀────── │ AlignmentSvc       │
   │             │             │                  │         │                    │
   │ • detects   │             │ • wraps          │         │ • calls RegimeSvc  │
   │   regime    │             │   run_allocation │         │ • calls AllocSvc   │
   │ • caches    │             │ • persists       │         │ • compares         │
   │ • persists  │             │   recommendation │         │ • NEVER detects    │
   └──────┬──────┘             └─────────┬────────┘         │ • NEVER optimizes  │
          │                              │                  └──────────┬─────────┘
          ▼                              ▼                             ▼
   ┌──────────────────────────────────────────────────────────────────────────┐
   │                           API Layer (FastAPI)                             │
   │                                                                           │
   │   GET  /api/v1/regime/current                                             │
   │   GET  /api/v1/allocation/recommended                                     │
   │   GET  /api/v1/allocation/history                                         │
   │   POST /api/v1/portfolio/alignment                                        │
   └──────────────────────────────────────┬────────────────────────────────────┘
                                          │
                                          ▼
   ┌──────────────────────────────────────────────────────────────────────────┐
   │                          UI Layer (React + TS)                            │
   │                                                                           │
   │   ① CurrentRegime   ② RecommendedAllocation                               │
   │   ③ PortfolioAlignment   ④ AllocationChanges                              │
   │                                                                           │
   │   Secondary: History · Analytics · Optimizer · Scenarios                  │
   └──────────────────────────────────────────────────────────────────────────┘
```

**Arrows point inward.** An inner layer never knows about an outer layer.
The UI knows about the API; the API knows about services; services know
about the engine. Never the reverse.

---

## 2. Logic Placement Rules

Each concern has exactly one home. Violations must be fixed at the source,
not worked around.

| Concern | Lives in | Must NOT appear in |
|---|---|---|
| Regime detection (HMM, features, probabilities) | `grine_regime_engine` | Services, API, UI |
| Strategic allocation (ranges, targeting, optimizer, turnover, dividends) | `grine_regime_engine.allocation` | Services, API, UI |
| Caching, persistence, tenant scoping | Services (`RegimeService`, `AllocationService`) | Engine, API, UI |
| Alignment scoring (deviations, range-status, score, adjustments) | `AlignmentService` | Engine, other services, UI |
| HTTP I/O, auth, tenant resolution | API layer | Services, UI |
| Presentation, layout, interaction | UI layer | Services, API |

**The alignment service is a comparator, not an engine.** It is
forbidden from:
- Calling `run_allocation()` or `RegimeEngine`
- Importing numpy, pandas, or cvxpy
- Redefining regime ranges, targets, or confidence thresholds
- Mutating persisted regime/allocation records

If a piece of logic feels like it belongs in two places, it belongs in
the lower layer, and the higher layer calls it.

---

## 3. Canonical Constants

**The following values are defined exactly once, in `grine_regime_engine`.
Nothing else may redefine them.**

### Regime states
`EXPANSION · BALANCED · TRANSITION · ENDURANCE · PROTECTION`

### Regime ranges (per spec)
| State | Equity | Bonds | Cash |
|---|---|---|---|
| EXPANSION | 0.60 – 0.70 | 0.20 – 0.30 | 0.00 – 0.05 |
| BALANCED | 0.45 – 0.55 | 0.35 – 0.45 | 0.05 – 0.10 |
| TRANSITION | 0.35 – 0.45 | 0.40 – 0.50 | 0.10 – 0.15 |
| ENDURANCE | 0.25 – 0.35 | 0.45 – 0.55 | 0.10 – 0.20 |
| PROTECTION | 0.20 – 0.30 | 0.50 – 0.60 | 0.15 – 0.25 |

### Turnover cap
`0.15` (L1). Configurable per tenant.

### Dividend share per regime
`EXPANSION 0-20% · BALANCED 20-40% · TRANSITION 50-60% · ENDURANCE 70-80% · PROTECTION 100%`

### Alignment scoring (single source: `AlignmentService`)
- `K1 = 50` — per-unit deviation penalty
- `K2 = 10` — discrete out-of-range penalty per sleeve
- Labels: `≥80 Highly Aligned · 55–79 Moderately Aligned · <55 Misaligned`

---

## 4. The 4 Canonical Endpoints

```
GET  /api/v1/regime/current              — what regime are we in?
GET  /api/v1/allocation/recommended      — what weights does doctrine say?
GET  /api/v1/allocation/history          — how has the recommendation moved?
POST /api/v1/portfolio/alignment         — how far am I from doctrine?
```

Every endpoint is tenant-scoped via `X-Tenant-ID` header or JWT claim.
No cross-tenant leakage.

---

## 5. UI Layout — Primary Surface

The main dashboard has **exactly four primary sections in this order**:

1. **Current Regime** (dominant; full-width)
2. **Recommended Allocation** (left column of section 2/3 split)
3. **Portfolio Alignment** (right column of section 2/3 split)
4. **Why It Changed** (full-width)

Secondary surfaces (History · Analytics · Optimizer · Scenarios) live in
a tab row below. They are tools, not the product.

Every element on the primary surface must answer:
**"What should I do with my capital?"**

If it doesn't, it belongs in secondary.

---

## 6. Forbidden Patterns

- ❌ Re-deriving regime ranges anywhere other than the engine
- ❌ Running regime detection inside `AlignmentService`
- ❌ Computing alignment score in the frontend
- ❌ Promoting optimizer/Sharpe/factor analytics to the primary surface
- ❌ Cross-tenant queries (every DB read must be filtered by `tenant_id`)
- ❌ Numpy/pandas in API handlers (the services wrap the engine)

---

## 7. Allowed Extensions

When new concerns arrive, they go in the appropriate layer:

- **New engine objective** (e.g. "ESG-tilted") → `grine_regime_engine.allocation.optimizer`
- **New data source** (e.g. per-tenant market feed) → `RegimeService`
- **New comparator dimension** (e.g. sector alignment) → extend `AlignmentService`
- **New endpoint** → `app/api/v1/*.py`, registered in `app/api/v1/__init__.py`
- **New UI surface** → components/ with its own folder, composed in `Dashboard.tsx`

If a contribution doesn't fit cleanly in one of these slots, the design
is wrong, not the rules.

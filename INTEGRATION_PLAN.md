# GrineOS Integration Plan — Doctrine-First Platform

**Objective:** Transform GrineOS from generic optimization to doctrine-first allocation platform powered by Grine regime detection and allocation engine.

## Current Structure (Inferred)
```
grineos/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # FastAPI endpoints
│   │   ├── models/          # Database models  
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   ├── main.py              # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/components/      # React components
│   ├── src/services/        # API clients
│   └── package.json
└── ai_agent/                # Claude integration
```

## Integration Phases

### **PHASE 1: BACKEND INTEGRATION**

#### Files to Create/Modify:
```
backend/
├── requirements.txt         # ADD: grine-regime-engine>=0.3.0
├── app/
│   ├── services/
│   │   ├── regime_service.py     # NEW: Regime detection service
│   │   └── allocation_service.py # NEW: Allocation engine service
│   ├── api/v1/
│   │   ├── regime.py        # NEW: GET /api/v1/regime/current
│   │   └── allocation.py    # NEW: GET /api/v1/allocation/*
│   ├── schemas/
│   │   ├── regime.py        # NEW: Regime response schemas
│   │   └── allocation.py    # NEW: Allocation response schemas
│   └── models/
│       ├── regime.py        # NEW: Regime history model
│       └── allocation.py    # NEW: Allocation history model
```

#### Key Changes:
1. **Add grine_regime_engine dependency**
2. **Create regime detection service** — wraps RegimeEngine with caching
3. **Create allocation service** — wraps run_allocation with portfolio state
4. **Add 3 new API endpoints** with tenant isolation
5. **Database models** for regime/allocation history

### **PHASE 2: FRONTEND INTEGRATION**

#### Files to Create/Modify:
```
frontend/src/
├── components/
│   ├── regime/
│   │   ├── CurrentRegime.tsx        # NEW: Current regime display
│   │   └── RegimeExplanation.tsx    # NEW: Why it changed
│   ├── allocation/
│   │   ├── RecommendedAllocation.tsx # NEW: Allocation display  
│   │   ├── AllocationBands.tsx       # NEW: Constraint bands
│   │   └── AllocationHistory.tsx     # NEW: Change history
│   └── dashboard/
│       └── MainDashboard.tsx         # MODIFY: Add regime section
├── services/
│   ├── regimeApi.ts         # NEW: Regime API client
│   └── allocationApi.ts     # NEW: Allocation API client
└── hooks/
    ├── useRegime.ts         # NEW: Regime data hook
    └── useAllocation.ts     # NEW: Allocation data hook
```

#### Key Changes:
1. **New dashboard sections** for Current Regime and Recommended Allocation
2. **Primary emphasis** on regime/allocation vs generic optimization
3. **Visual components** for constraint bands and confidence
4. **Real-time updates** with WebSocket or polling

### **PHASE 3: AI AGENT INTEGRATION**

#### Files to Create/Modify:
```
ai_agent/
├── tools/
│   ├── regime_tools.py      # NEW: Regime detection tools
│   └── allocation_tools.py  # NEW: Allocation tools  
├── prompts/
│   └── system_prompt.py     # MODIFY: Lead with regime/allocation
└── handlers/
    └── portfolio_handler.py # MODIFY: Always check regime first
```

#### Key Changes:
1. **Tool-first approach** — AI always calls regime/allocation tools
2. **Explain engine results** — never override regime recommendations  
3. **Standard responses** for common questions about regime changes

### **PHASE 4: PRODUCT REPOSITIONING**

#### Files to Modify:
```
frontend/src/
├── components/navigation/   # Update labels
├── pages/                   # Reorder priority  
└── copy/                    # "GrineOS — the OS for capital allocation"

backend/app/api/v1/
├── optimizer.py            # REPOSITION as secondary tool
└── scenarios.py            # REPOSITION under allocation framework
```

#### Key Changes:
1. **Update UI copy** — emphasize allocation doctrine
2. **Reorder navigation** — regime/allocation first
3. **Reposition existing tools** as secondary under Grine framework

## Implementation Order

1. **Phase 1** (Backend) — 2-3 days
2. **Phase 2** (Frontend) — 3-4 days  
3. **Phase 3** (AI Agent) — 1-2 days
4. **Phase 4** (Repositioning) — 1 day

Total: **7-10 days** for full integration

## Risk Mitigation

- **Feature flags** for gradual rollout
- **A/B testing** between old/new dashboard
- **Backward compatibility** for existing API clients
- **Database migrations** for new models
- **Comprehensive testing** of tenant isolation

## Success Metrics

- **Regime detection accuracy** (85%+ on backtests)
- **API response times** (<200ms for regime/allocation)
- **User engagement** with new dashboard sections
- **AI agent usage** of regime tools (90%+ of portfolio conversations)

Ready to begin implementation?

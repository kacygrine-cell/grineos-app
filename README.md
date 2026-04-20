# GrineOS
> The Operating System for Capital Allocation

GrineOS is a doctrine-first portfolio allocation system that combines regime detection, strategic allocation, and alignment scoring into a unified decision-making framework.
## What GrineOS Does

GrineOS answers three critical questions for capital allocation:

1. **What regime are we in?** → Real-time market state classification across 5 regimes
2. **How should capital be allocated?** → Strategic weights within regime-appropriate constraint bands  
3. **How aligned is a portfolio with that allocation?** → Transparent scoring with actionable adjustments

It combines:
- Regime detection using ensemble HMM methods
- Constraint-based allocation optimization  
- Portfolio alignment scoring with transparent penalties

into a unified decision framework.
## Architecture
grine_regime_engine  →  Backend Services  →  React Dashboard
(detection)         (allocation +          (decision
alignment)              surface)
## Features

- **Regime Detection**: 5 market states (EXPANSION/BALANCED/TRANSITION/ENDURANCE/PROTECTION)
- **Strategic Allocation**: Regime-based constraint bands with turnover management
- **Alignment Scoring**: Transparent K1/K2 penalty system with 80/55 thresholds
- **Multi-tenant API**: FastAPI with Redis caching and PostgreSQL
- **Editorial UI**: Typography-first React dashboard with Fraunces serif

## Quick Start

```bash
git clone https://github.com/kacygrine-cell/grineos-app.git
cd grineos-app

# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (new terminal)  
cd frontend
npm install && npm run dev
```

Visit `http://localhost:3000`

## API Endpoints

- `GET /api/v1/regime/current` — Current market regime detection
- `GET /api/v1/allocation/recommended` — Strategic allocation weights
- `GET /api/v1/allocation/history` — Allocation change history
- `POST /api/v1/portfolio/alignment` — Portfolio alignment scoring

## Documentation

- [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) — Canonical system design rules
- [**INTEGRATION_COMPLETE.md**](INTEGRATION_COMPLETE.md) — Build summary and validation

## Status

- ✅ 45 passing tests including 5-scenario validation  
- ✅ Production-ready backend + frontend
- ✅ Complete integrated system
- 🚧 Production deployment
- 📋 AI agent integration

Built by [Kacy](https://github.com/kacygrine-cell) using Claude as the core technical execution layer.

## License

MIT License

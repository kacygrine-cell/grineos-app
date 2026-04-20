# GrineOS
> The Operating System for Capital Allocation

> GrineOS provides a consistent framework to define, evaluate, and adjust portfolio allocation across market regimes.

GrineOS is a doctrine-first portfolio allocation system that combines regime detection, strategic allocation, and alignment scoring into a unified decision-making framework.
## What GrineOS Does

GrineOS answers three critical questions for capital allocation:

1. **What regime are we in?** → Real-time market state classification across 5 regimes
2. **How should capital be allocated?** → Strategic weights within regime-appropriate constraint bands  
3. **How aligned is a portfolio with that allocation?** → Transparent scoring with actionable adjustments

It combines:
- Regime detection using ensemble HMM methods
- Constraint-based allocation within defined regime bands  
- Portfolio alignment scoring with transparent penalties

into a unified decision framework.

GrineOS is not a trading system or an optimizer.
It is a decision framework for capital allocation.    
## Why GrineOS Exists

Capital allocation today lacks a consistent framework.

- Market regimes are identified inconsistently  
- Allocation decisions are often discretionary or opaque  
- Portfolio alignment is rarely measured in a structured way  

As a result, portfolios drift away from their intended strategy without a clear framework to detect or correct it.

GrineOS solves this by providing a unified system that defines:
- the current market regime
- the appropriate allocation
- and the degree of alignment of any portfolio to that allocation
## Architecture
## System Flow

Regime → Allocation → Alignment → Decision

GrineOS transforms market data into a structured allocation decision:

1. Regime detection identifies the current market state  
2. Allocation defines appropriate portfolio ranges  
3. Alignment measures how a portfolio compares  
4. The system surfaces clear actions
## Features

- **Regime Detection**: 5 market states (EXPANSION/BALANCED/TRANSITION/ENDURANCE/PROTECTION)
- **Strategic Allocation**: Regime-based constraint bands with turnover management
- **Alignment Scoring**: Transparent scoring system with clear thresholds and actionable adjustements
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

## Positioning

GrineOS defines a structured framework for capital allocation.

It sits above:
- market data providers
- index providers
- asset managers

and provides a consistent reference layer for allocation decisions across all of them.

Developed by Kacy.

## Vision

GrineOS aims to become a standard framework for capital allocation, where portfolios, mandates and strategies are evaluated relative to a common regime-based system.

## License

MIT License

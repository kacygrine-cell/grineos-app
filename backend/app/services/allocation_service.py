"""Allocation engine service with caching and tenant isolation."""
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from grine_regime_engine.allocation import (
    run_allocation,
    RegimeSnapshot,
    RegimeState,
    AssetUniverse
)

from app.core.config import settings
from app.models.allocation import (
    AllocationRecommendation, 
    PortfolioState, 
    AllocationChange
)
from app.models.regime import RegimeDetection
from app.models.user import Tenant
from app.services.regime_service import RegimeService


class AllocationService:
    """Service for portfolio allocation with caching and persistence."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client or redis.from_url(settings.REDIS_URL)
        self.regime_service = RegimeService(redis_client)
    
    async def get_recommended_allocation(
        self,
        tenant_id: UUID,
        session: AsyncSession,
        force_refresh: bool = False,
        objective: Optional[str] = None,
        turnover_cap: Optional[float] = None
    ) -> Optional[AllocationRecommendation]:
        """Get recommended allocation for a tenant."""
        cache_key = f"allocation:recommended:{tenant_id}"
        
        # Try cache first (unless forcing refresh)
        if not force_refresh:
            cached = await self._get_cached_allocation(cache_key)
            if cached:
                return cached
        
        # Get current regime
        regime_detection = await self.regime_service.get_current_regime(
            tenant_id, session, force_refresh
        )
        if not regime_detection:
            return None
        
        # Get current portfolio state
        portfolio_state = await self._get_portfolio_state(tenant_id, session)
        
        # Get tenant settings
        tenant = await self._get_tenant_settings(tenant_id, session)
        
        # Prepare parameters
        objective = objective or (tenant.default_optimizer if tenant else settings.DEFAULT_OPTIMIZER_OBJECTIVE)
        turnover_cap = turnover_cap or (tenant.default_turnover_cap if tenant else settings.DEFAULT_TURNOVER_CAP)
        
        # Run allocation engine
        start_time = time.time()
        allocation = await self._run_allocation_engine(
            regime_detection, portfolio_state, objective, turnover_cap, tenant_id, session
        )
        
        if allocation:
            processing_time = (time.time() - start_time) * 1000
            allocation.processing_time_ms = processing_time
            
            # Cache the result
            await self._cache_allocation(cache_key, allocation)
            
            # Update portfolio state
            await self._update_portfolio_state(tenant_id, allocation, session)
            
            # Check for significant changes
            await self._check_for_allocation_change(tenant_id, allocation, session)
        
        return allocation
    
    async def get_allocation_history(
        self,
        tenant_id: UUID,
        session: AsyncSession,
        days_lookback: int = 30,
        limit: int = 50
    ) -> List[AllocationRecommendation]:
        """Get allocation history for a tenant."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_lookback)
        
        stmt = select(AllocationRecommendation).where(
            AllocationRecommendation.tenant_id == tenant_id,
            AllocationRecommendation.created_at >= cutoff_date
        ).order_by(
            AllocationRecommendation.created_at.desc()
        ).limit(limit)
        
        result = await session.execute(stmt)
        return result.scalars().all()
    
    async def _get_portfolio_state(
        self, 
        tenant_id: UUID, 
        session: AsyncSession
    ) -> Optional[Dict[str, float]]:
        """Get current portfolio weights for turnover calculation."""
        stmt = select(PortfolioState).where(
            PortfolioState.tenant_id == tenant_id
        )
        
        result = await session.execute(stmt)
        portfolio = result.scalar_one_or_none()
        
        if portfolio:
            return {
                "equity": portfolio.current_equity,
                "bonds": portfolio.current_bonds,
                "cash": portfolio.current_cash
            }
        
        # Default starting portfolio (conservative)
        return {"equity": 0.40, "bonds": 0.50, "cash": 0.10}
    
    async def _get_tenant_settings(
        self, 
        tenant_id: UUID, 
        session: AsyncSession
    ) -> Optional[Any]:
        """Get tenant-specific allocation settings."""
        from app.models.user import Tenant
        
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _run_allocation_engine(
        self,
        regime_detection: RegimeDetection,
        previous_weights: Optional[Dict[str, float]],
        objective: str,
        turnover_cap: float,
        tenant_id: UUID,
        session: AsyncSession
    ) -> Optional[AllocationRecommendation]:
        """Run the allocation engine."""
        try:
            # Create regime snapshot
            regime_snapshot = RegimeSnapshot(
                final_state=regime_detection.final_state,
                probabilities=regime_detection.probabilities.get("raw") if regime_detection.probabilities else None,
                confidence=regime_detection.confidence,
                momentum=regime_detection.momentum
            )
            
            # Default asset universe (can be customized per tenant later)
            asset_universe = AssetUniverse()
            
            # Run allocation (CPU-bound, run in thread)
            loop = asyncio.get_event_loop()
            allocation_result = await loop.run_in_executor(
                None,
                run_allocation,
                regime_snapshot,
                previous_weights,
                asset_universe,
                objective,
                0.25,  # momentum_weight
                0.5,   # tracking_weight
                turnover_cap
            )
            
            # Analyze change magnitude and reason
            change_reason, change_magnitude = await self._analyze_allocation_change(
                tenant_id, allocation_result, previous_weights, regime_detection, session
            )
            
            # Create database record
            recommendation = AllocationRecommendation(
                tenant_id=tenant_id,
                regime_detection_id=regime_detection.id,
                
                # Final weights
                equity_weight=allocation_result["final_weights"]["equity"],
                bonds_weight=allocation_result["final_weights"]["bonds"],
                cash_weight=allocation_result["final_weights"]["cash"],
                
                # Target weights
                target_equity=allocation_result["target_weights"]["equity"],
                target_bonds=allocation_result["target_weights"]["bonds"],
                target_cash=allocation_result["target_weights"]["cash"],
                
                # Previous weights (for audit)
                previous_equity=previous_weights.get("equity") if previous_weights else None,
                previous_bonds=previous_weights.get("bonds") if previous_weights else None,
                previous_cash=previous_weights.get("cash") if previous_weights else None,
                
                # Constraints
                constraints=allocation_result["constraints"],
                
                # Turnover
                turnover_realized=allocation_result["turnover"]["realized"],
                turnover_proposed=allocation_result["turnover"]["proposed"],
                turnover_capped=allocation_result["turnover"]["capped"],
                turnover_cap=allocation_result["turnover"]["cap"],
                
                # Dividend split
                dividend_growth_weight=allocation_result["dividend_split"]["growth"],
                dividend_income_weight=allocation_result["dividend_split"]["dividend"],
                dividend_share=allocation_result["dividend_split"]["dividend_share"],
                dividend_range_lower=allocation_result["dividend_split"]["range_lower"],
                dividend_range_upper=allocation_result["dividend_split"]["range_upper"],
                
                # Engine parameters
                optimizer_objective=allocation_result["constraints"]["objective"],
                optimizer_status=allocation_result["constraints"]["optimizer_status"],
                
                # Change analysis
                change_reason=change_reason,
                change_magnitude=change_magnitude,
                
                cache_hit=False
            )
            
            session.add(recommendation)
            await session.commit()
            await session.refresh(recommendation)
            
            return recommendation
            
        except Exception as e:
            print(f"Allocation engine failed: {e}")
            return None
    
    async def _analyze_allocation_change(
        self,
        tenant_id: UUID,
        allocation_result: Dict[str, Any],
        previous_weights: Optional[Dict[str, float]],
        regime_detection: RegimeDetection,
        session: AsyncSession
    ) -> tuple[Optional[str], Optional[str]]:
        """Analyze why the allocation changed and how significant the change is."""
        if not previous_weights:
            return "Initial allocation", "initial"
        
        # Calculate total change (L1 norm)
        current = allocation_result["final_weights"]
        total_change = sum(
            abs(current[asset] - previous_weights[asset])
            for asset in ["equity", "bonds", "cash"]
        )
        
        # Classify magnitude
        if total_change < 0.02:
            magnitude = "minor"
        elif total_change < 0.10:
            magnitude = "moderate"
        else:
            magnitude = "major"
        
        # Generate reason
        regime_state = allocation_result["constraints"]["regime_state"]
        confidence = regime_detection.confidence
        momentum = regime_detection.momentum
        
        # Simple heuristic for change reason
        if allocation_result["turnover"]["capped"]:
            reason = f"Gradual move toward {regime_state} regime (turnover capped at {allocation_result['turnover']['cap']:.0%})"
        elif confidence > 0.7:
            if momentum > 0.3:
                reason = f"High confidence {regime_state} regime with strong positive momentum"
            elif momentum < -0.3:
                reason = f"High confidence {regime_state} regime with negative momentum"
            else:
                reason = f"High confidence {regime_state} regime detected"
        elif confidence < 0.3:
            reason = f"Low confidence regime detection, conservative positioning"
        else:
            reason = f"Moderate confidence {regime_state} regime with balanced positioning"
        
        return reason, magnitude
    
    async def _get_cached_allocation(self, cache_key: str) -> Optional[AllocationRecommendation]:
        """Get allocation from cache."""
        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                # Reconstruct AllocationRecommendation from cached data
                recommendation = AllocationRecommendation(**data)
                recommendation.cache_hit = True
                return recommendation
        except Exception:
            pass
        return None
    
    async def _cache_allocation(
        self, 
        cache_key: str, 
        recommendation: AllocationRecommendation
    ) -> None:
        """Cache allocation recommendation."""
        try:
            # Convert to dict for JSON serialization
            data = {
                "id": str(recommendation.id),
                "tenant_id": str(recommendation.tenant_id),
                "regime_detection_id": str(recommendation.regime_detection_id),
                "equity_weight": recommendation.equity_weight,
                "bonds_weight": recommendation.bonds_weight,
                "cash_weight": recommendation.cash_weight,
                "target_equity": recommendation.target_equity,
                "target_bonds": recommendation.target_bonds,
                "target_cash": recommendation.target_cash,
                "constraints": recommendation.constraints,
                "turnover_realized": recommendation.turnover_realized,
                "turnover_proposed": recommendation.turnover_proposed,
                "turnover_capped": recommendation.turnover_capped,
                "turnover_cap": recommendation.turnover_cap,
                "dividend_growth_weight": recommendation.dividend_growth_weight,
                "dividend_income_weight": recommendation.dividend_income_weight,
                "dividend_share": recommendation.dividend_share,
                "dividend_range_lower": recommendation.dividend_range_lower,
                "dividend_range_upper": recommendation.dividend_range_upper,
                "optimizer_objective": recommendation.optimizer_objective,
                "optimizer_status": recommendation.optimizer_status,
                "change_reason": recommendation.change_reason,
                "change_magnitude": recommendation.change_magnitude,
                "processing_time_ms": recommendation.processing_time_ms,
                "created_at": recommendation.created_at.isoformat()
            }
            
            await self.redis.setex(
                cache_key,
                settings.ALLOCATION_CACHE_TTL,
                json.dumps(data, default=str)
            )
        except Exception:
            pass
    
    async def _update_portfolio_state(
        self,
        tenant_id: UUID,
        recommendation: AllocationRecommendation,
        session: AsyncSession
    ) -> None:
        """Update the portfolio state with new allocation."""
        try:
            # Get or create portfolio state
            stmt = select(PortfolioState).where(
                PortfolioState.tenant_id == tenant_id
            )
            result = await session.execute(stmt)
            portfolio = result.scalar_one_or_none()
            
            if not portfolio:
                portfolio = PortfolioState(
                    tenant_id=tenant_id,
                    inception_date=datetime.utcnow()
                )
                session.add(portfolio)
            
            # Update with new allocation
            portfolio.current_equity = recommendation.equity_weight
            portfolio.current_bonds = recommendation.bonds_weight
            portfolio.current_cash = recommendation.cash_weight
            portfolio.last_recommendation_id = recommendation.id
            portfolio.last_rebalanced_at = datetime.utcnow()
            
            await session.commit()
            
        except Exception:
            pass
    
    async def _check_for_allocation_change(
        self,
        tenant_id: UUID,
        current_recommendation: AllocationRecommendation,
        session: AsyncSession
    ) -> None:
        """Check for significant allocation changes and record them."""
        try:
            # Get the previous recommendation
            stmt = select(AllocationRecommendation).where(
                AllocationRecommendation.tenant_id == tenant_id,
                AllocationRecommendation.id != current_recommendation.id
            ).order_by(AllocationRecommendation.created_at.desc()).limit(1)
            
            result = await session.execute(stmt)
            prev_recommendation = result.scalar_one_or_none()
            
            if prev_recommendation:
                # Calculate changes
                equity_change = current_recommendation.equity_weight - prev_recommendation.equity_weight
                bonds_change = current_recommendation.bonds_weight - prev_recommendation.bonds_weight
                cash_change = current_recommendation.cash_weight - prev_recommendation.cash_weight
                total_change = abs(equity_change) + abs(bonds_change) + abs(cash_change)
                
                # Record significant changes (>2% total)
                if total_change > 0.02:
                    change = AllocationChange(
                        tenant_id=tenant_id,
                        from_recommendation_id=prev_recommendation.id,
                        to_recommendation_id=current_recommendation.id,
                        equity_change=equity_change,
                        bonds_change=bonds_change,
                        cash_change=cash_change,
                        total_change=total_change,
                        change_type="regime_shift",  # Could be more sophisticated
                        change_magnitude=current_recommendation.change_magnitude,
                        explanation=current_recommendation.change_reason
                    )
                    
                    session.add(change)
                    await session.commit()
                    
        except Exception:
            pass

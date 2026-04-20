"""Regime detection service with caching and tenant isolation."""
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID

import numpy as np
import pandas as pd
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from grine_regime_engine import RegimeEngine, GaussianHMMDetector
from grine_regime_engine.allocation import RegimeSnapshot
from grine_regime_engine.allocation.targeting import (
    compute_momentum_from_returns,
    confidence_from_probabilities
)

from app.core.config import settings
from app.models.regime import RegimeDetection, RegimeTransition, MarketData
from app.models.user import Tenant


class RegimeService:
    """Service for regime detection with caching and persistence."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client or redis.from_url(settings.REDIS_URL)
        # Initialize regime engine (cached per instance)
        self._engine = None
    
    @property
    def engine(self) -> RegimeEngine:
        """Lazy-loaded regime engine."""
        if self._engine is None:
            detector = GaussianHMMDetector(n_regimes=3, random_state=42)
            self._engine = RegimeEngine(detector)
        return self._engine
    
    async def get_current_regime(
        self,
        tenant_id: UUID,
        session: AsyncSession,
        force_refresh: bool = False
    ) -> Optional[RegimeDetection]:
        """Get current regime for a tenant."""
        cache_key = f"regime:current:{tenant_id}"
        
        # Try cache first (unless forcing refresh)
        if not force_refresh:
            cached = await self._get_cached_regime(cache_key)
            if cached:
                return cached
        
        # Get market data for tenant
        market_data = await self._get_market_data(tenant_id, session)
        if not market_data or len(market_data) < 50:
            # Not enough data for regime detection
            return None
        
        # Run regime detection
        start_time = time.time()
        detection = await self._run_regime_detection(
            market_data, tenant_id, session
        )
        
        if detection:
            processing_time = (time.time() - start_time) * 1000
            detection.processing_time_ms = processing_time
            
            # Cache the result
            await self._cache_regime(cache_key, detection)
            
            # Check for regime transitions
            await self._check_for_transition(tenant_id, detection, session)
        
        return detection
    
    async def _get_market_data(
        self, 
        tenant_id: UUID, 
        session: AsyncSession,
        days_lookback: int = 500
    ) -> Optional[pd.Series]:
        """Get market data for regime detection."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_lookback)
        
        # Query market data for the tenant
        stmt = select(MarketData).where(
            MarketData.tenant_id == tenant_id,
            MarketData.date >= cutoff_date,
            MarketData.symbol == "SPY"  # Default to S&P 500
        ).order_by(MarketData.date)
        
        result = await session.execute(stmt)
        data = result.scalars().all()
        
        if not data:
            # Fallback: generate synthetic data for demo
            return await self._generate_demo_data()
        
        # Convert to pandas Series
        dates = [d.date for d in data]
        prices = [d.close_price for d in data]
        return pd.Series(prices, index=pd.DatetimeIndex(dates))
    
    async def _generate_demo_data(self) -> pd.Series:
        """Generate demo market data for testing."""
        # Create 500 days of synthetic market data
        np.random.seed(42)
        dates = pd.date_range(end=datetime.utcnow(), periods=500, freq="D")
        
        # Multi-regime synthetic returns
        segments = [
            (150, 0.0008, 0.012),  # Bull market
            (100, 0.0002, 0.018),  # Choppy
            (80, -0.0015, 0.025),  # Bear market  
            (120, 0.0012, 0.015),  # Recovery
            (50, 0.0006, 0.011),   # Continuation
        ]
        
        returns = []
        for n_days, mu, sigma in segments:
            segment_returns = np.random.normal(mu, sigma, n_days)
            returns.extend(segment_returns)
        
        # Convert to price series
        returns = returns[:len(dates)]  # Ensure same length
        prices = 100 * np.exp(np.cumsum(returns))
        
        return pd.Series(prices, index=dates)
    
    async def _run_regime_detection(
        self,
        price_data: pd.Series,
        tenant_id: UUID,
        session: AsyncSession
    ) -> Optional[RegimeDetection]:
        """Run the regime detection engine."""
        try:
            # Run regime detection (CPU-bound, run in thread)
            loop = asyncio.get_event_loop()
            regime_result = await loop.run_in_executor(
                None, 
                self.engine.run, 
                price_data
            )
            
            # Extract results
            assignment = regime_result.assignment
            if assignment.labels is None or len(assignment.labels) == 0:
                return None
            
            last_label = int(assignment.labels[-1])
            regime = regime_result.labels.label(last_label)
            
            # Calculate derived metrics
            returns = price_data.pct_change().dropna()
            momentum = compute_momentum_from_returns(returns.values)
            
            probs = None
            confidence = 0.5
            if assignment.probabilities is not None:
                probs = assignment.probabilities[-1]
                confidence = confidence_from_probabilities(np.array(probs))
            
            # Map regime to strategic state
            regime_snapshot = RegimeSnapshot(
                final_state=regime,
                probabilities=[float(p) for p in probs] if probs is not None else None,
                confidence=confidence,
                momentum=momentum
            )
            
            # Create database record
            detection = RegimeDetection(
                tenant_id=tenant_id,
                final_state=regime_snapshot.final_state.value if hasattr(regime_snapshot.final_state, 'value') else str(regime_snapshot.final_state),
                raw_regime=regime.value,
                confidence=confidence,
                momentum=momentum,
                probabilities={
                    "raw": [float(p) for p in probs] if probs is not None else None,
                    "bull": float(probs[0]) if probs is not None and len(probs) > 0 else 0.0,
                    "bear": float(probs[1]) if probs is not None and len(probs) > 1 else 0.0,
                    "crisis": float(probs[2]) if probs is not None and len(probs) > 2 else 0.0,
                },
                detector_type="GaussianHMM",
                n_regimes=3,
                data_start_date=price_data.index[0].to_pydatetime(),
                data_end_date=price_data.index[-1].to_pydatetime(),
                data_points=len(price_data),
                cache_hit=False
            )
            
            session.add(detection)
            await session.commit()
            await session.refresh(detection)
            
            return detection
            
        except Exception as e:
            print(f"Regime detection failed: {e}")
            return None
    
    async def _get_cached_regime(self, cache_key: str) -> Optional[RegimeDetection]:
        """Get regime from cache."""
        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                # Reconstruct RegimeDetection from cached data
                detection = RegimeDetection(**data)
                detection.cache_hit = True
                return detection
        except Exception:
            pass
        return None
    
    async def _cache_regime(self, cache_key: str, detection: RegimeDetection) -> None:
        """Cache regime detection result."""
        try:
            # Convert to dict for JSON serialization
            data = {
                "id": str(detection.id),
                "tenant_id": str(detection.tenant_id),
                "final_state": detection.final_state,
                "raw_regime": detection.raw_regime,
                "confidence": detection.confidence,
                "momentum": detection.momentum,
                "probabilities": detection.probabilities,
                "detector_type": detection.detector_type,
                "n_regimes": detection.n_regimes,
                "data_start_date": detection.data_start_date.isoformat() if detection.data_start_date else None,
                "data_end_date": detection.data_end_date.isoformat() if detection.data_end_date else None,
                "data_points": detection.data_points,
                "processing_time_ms": detection.processing_time_ms,
                "created_at": detection.created_at.isoformat()
            }
            
            await self.redis.setex(
                cache_key,
                settings.REGIME_CACHE_TTL,
                json.dumps(data, default=str)
            )
        except Exception:
            pass  # Cache failure shouldn't break the service
    
    async def _check_for_transition(
        self,
        tenant_id: UUID,
        current_detection: RegimeDetection,
        session: AsyncSession
    ) -> None:
        """Check for regime transitions and record them."""
        try:
            # Get the previous detection
            stmt = select(RegimeDetection).where(
                RegimeDetection.tenant_id == tenant_id,
                RegimeDetection.id != current_detection.id
            ).order_by(RegimeDetection.created_at.desc()).limit(1)
            
            result = await session.execute(stmt)
            prev_detection = result.scalar_one_or_none()
            
            if prev_detection and prev_detection.final_state != current_detection.final_state:
                # Regime transition detected
                transition = RegimeTransition(
                    tenant_id=tenant_id,
                    from_state=prev_detection.final_state,
                    to_state=current_detection.final_state,
                    confidence_change=current_detection.confidence - prev_detection.confidence,
                    momentum_change=current_detection.momentum - prev_detection.momentum,
                    from_detection_id=prev_detection.id,
                    to_detection_id=current_detection.id
                )
                
                session.add(transition)
                await session.commit()
                
        except Exception:
            pass  # Transition tracking failure shouldn't break the service

"""Regime detection API endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.regime import RegimeResponse, RegimeMetadata, RegimeProbabilities
from app.services.regime_service import RegimeService
from app.api.dependencies import get_current_tenant_id

router = APIRouter()


@router.get("/current", response_model=RegimeResponse)
async def get_current_regime(
    tenant_id: UUID = Depends(get_current_tenant_id),
    force_refresh: bool = Query(False, description="Force refresh regime detection"),
    session: AsyncSession = Depends(get_session)
):
    """
    Get current market regime for the tenant.
    
    Returns the latest regime detection including:
    - Strategic regime state (EXPANSION, BALANCED, etc.)
    - Raw regime label (bull, bear, crisis, etc.)  
    - Confidence score (0-1)
    - Market momentum (-1 to +1)
    - Regime probabilities
    - Detection metadata
    """
    regime_service = RegimeService()
    
    detection = await regime_service.get_current_regime(
        tenant_id, session, force_refresh
    )
    
    if not detection:
        raise HTTPException(
            status_code=404,
            detail="Unable to detect current regime. Insufficient market data."
        )
    
    # Build probabilities
    probabilities = None
    if detection.probabilities and "raw" in detection.probabilities:
        raw_probs = detection.probabilities["raw"]
        if raw_probs and len(raw_probs) >= 3:
            probabilities = RegimeProbabilities(
                bull=detection.probabilities.get("bull", raw_probs[0]),
                bear=detection.probabilities.get("bear", raw_probs[1]),
                crisis=detection.probabilities.get("crisis", raw_probs[2])
            )
    
    # Build metadata
    metadata = RegimeMetadata(
        detector_type=detection.detector_type,
        n_regimes=detection.n_regimes,
        data_start_date=detection.data_start_date,
        data_end_date=detection.data_end_date,
        data_points=detection.data_points,
        processing_time_ms=detection.processing_time_ms,
        cache_hit=detection.cache_hit
    )
    
    return RegimeResponse(
        final_state=detection.final_state,
        raw_regime=detection.raw_regime,
        confidence=detection.confidence,
        momentum=detection.momentum,
        probabilities=probabilities,
        metadata=metadata,
        detection_id=detection.id,
        tenant_id=detection.tenant_id,
        created_at=detection.created_at
    )


@router.get("/health")
async def regime_health_check():
    """Health check for regime detection service."""
    return {
        "status": "healthy",
        "service": "regime_detection",
        "engine": "grine_regime_engine v0.3.0"
    }

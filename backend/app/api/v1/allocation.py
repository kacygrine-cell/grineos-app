"""Allocation engine API endpoints."""
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.allocation import (
    AllocationResponse,
    AllocationHistoryResponse,
    AllocationWeights,
    AllocationRanges,
    AllocationConstraints,
    TurnoverInfo,
    DividendSplit,
    AllocationHistoryItem
)
from app.services.allocation_service import AllocationService
from app.api.dependencies import get_current_tenant_id

router = APIRouter()


@router.get("/recommended", response_model=AllocationResponse)
async def get_recommended_allocation(
    tenant_id: UUID = Depends(get_current_tenant_id),
    force_refresh: bool = Query(False, description="Force refresh allocation calculation"),
    objective: Optional[str] = Query(None, description="Optimizer objective: min_variance, max_sharpe, risk_parity"),
    turnover_cap: Optional[float] = Query(None, ge=0.01, le=0.50, description="L1 turnover cap (0.01-0.50)"),
    session: AsyncSession = Depends(get_session)
):
    """
    Get recommended portfolio allocation for the tenant.
    
    Returns the latest allocation recommendation including:
    - Final recommended weights (equity/bonds/cash)
    - Target weights before turnover constraints
    - Constraint bands based on current regime
    - Turnover analysis (realized vs proposed)
    - Dividend/growth split within equity
    - Change analysis and explanation
    """
    allocation_service = AllocationService()
    
    recommendation = await allocation_service.get_recommended_allocation(
        tenant_id=tenant_id,
        session=session,
        force_refresh=force_refresh,
        objective=objective,
        turnover_cap=turnover_cap
    )
    
    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail="Unable to generate allocation recommendation. Check regime detection."
        )
    
    # Build response components
    final_weights = AllocationWeights(
        equity=recommendation.equity_weight,
        bonds=recommendation.bonds_weight,
        cash=recommendation.cash_weight
    )
    
    target_weights = AllocationWeights(
        equity=recommendation.target_equity,
        bonds=recommendation.target_bonds,
        cash=recommendation.target_cash
    )
    
    constraints_data = recommendation.constraints
    constraints = AllocationConstraints(
        regime_state=constraints_data["regime_state"],
        ranges=AllocationRanges(**constraints_data["ranges"]),
        turnover_cap=constraints_data["turnover_cap"],
        objective=constraints_data["objective"],
        optimizer_status=constraints_data["optimizer_status"]
    )
    
    turnover = TurnoverInfo(
        realized=recommendation.turnover_realized,
        proposed=recommendation.turnover_proposed,
        cap=recommendation.turnover_cap,
        capped=recommendation.turnover_capped
    )
    
    dividend_split = DividendSplit(
        equity_total=recommendation.equity_weight,
        growth=recommendation.dividend_growth_weight,
        dividend=recommendation.dividend_income_weight,
        dividend_share=recommendation.dividend_share,
        range_lower=recommendation.dividend_range_lower,
        range_upper=recommendation.dividend_range_upper
    )
    
    return AllocationResponse(
        final_weights=final_weights,
        target_weights=target_weights,
        constraints=constraints,
        turnover=turnover,
        dividend_split=dividend_split,
        change_reason=recommendation.change_reason,
        change_magnitude=recommendation.change_magnitude,
        recommendation_id=recommendation.id,
        regime_detection_id=recommendation.regime_detection_id,
        tenant_id=recommendation.tenant_id,
        created_at=recommendation.created_at,
        processing_time_ms=recommendation.processing_time_ms
    )


@router.get("/history", response_model=AllocationHistoryResponse)
async def get_allocation_history(
    tenant_id: UUID = Depends(get_current_tenant_id),
    days_lookback: int = Query(30, ge=1, le=365, description="Days of history to retrieve"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records"),
    session: AsyncSession = Depends(get_session)
):
    """
    Get allocation history for the tenant.
    
    Returns:
    - Current allocation recommendation (most recent)
    - Historical allocations over the specified period
    - Aggregate statistics (turnover, regime distribution, etc.)
    - Date range and total count
    """
    allocation_service = AllocationService()
    
    # Get current recommendation
    current = await allocation_service.get_recommended_allocation(
        tenant_id=tenant_id,
        session=session,
        force_refresh=False
    )
    
    if not current:
        raise HTTPException(
            status_code=404,
            detail="No allocation history found for tenant"
        )
    
    # Get historical allocations
    history_records = await allocation_service.get_allocation_history(
        tenant_id=tenant_id,
        session=session,
        days_lookback=days_lookback,
        limit=limit
    )
    
    # Build current allocation response
    current_response = await get_recommended_allocation(
        tenant_id=tenant_id,
        session=session
    )
    
    # Build history items (simplified format)
    history_items = []
    for record in history_records[1:]:  # Skip first (current) record
        item = AllocationHistoryItem(
            recommendation_id=record.id,
            weights=AllocationWeights(
                equity=record.equity_weight,
                bonds=record.bonds_weight,
                cash=record.cash_weight
            ),
            regime_state=record.constraints["regime_state"],
            confidence=0.5,  # Would need to join with regime detection
            momentum=0.0,    # Would need to join with regime detection  
            turnover=record.turnover_realized,
            change_magnitude=record.change_magnitude,
            created_at=record.created_at
        )
        history_items.append(item)
    
    # Calculate aggregate statistics
    if history_records:
        avg_turnover = sum(r.turnover_realized for r in history_records) / len(history_records)
        regime_states = [r.constraints["regime_state"] for r in history_records]
        regime_distribution = {
            state: regime_states.count(state) / len(regime_states)
            for state in set(regime_states)
        }
        rebalance_frequency = len(history_records) / max(days_lookback, 1)
        
        stats = {
            "avg_turnover": avg_turnover,
            "regime_distribution": regime_distribution,
            "rebalance_frequency": rebalance_frequency
        }
    else:
        stats = {
            "avg_turnover": 0.0,
            "regime_distribution": {},
            "rebalance_frequency": 0.0
        }
    
    # Date range
    date_range = {}
    if history_records:
        date_range = {
            "start": history_records[-1].created_at,
            "end": history_records[0].created_at
        }
    
    return AllocationHistoryResponse(
        current=current_response,
        history=history_items,
        total_count=len(history_records),
        date_range=date_range,
        stats=stats
    )


@router.get("/health")
async def allocation_health_check():
    """Health check for allocation service."""
    return {
        "status": "healthy",
        "service": "allocation_engine",
        "engine": "grine_regime_engine v0.3.0"
    }

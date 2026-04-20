"""Portfolio alignment API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_tenant_id
from app.core.database import get_session
from app.schemas.portfolio import AlignmentRequest, AlignmentResponse, PortfolioWeights
from app.services.alignment_service import AlignmentService

router = APIRouter()


@router.post("/alignment", response_model=AlignmentResponse)
async def post_portfolio_alignment(
    body: AlignmentRequest,
    tenant_id: UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Compute portfolio alignment against the current Grine doctrine.

    Input: asset-class weights (equity / bonds / cash) — must sum to ~1.0.

    The endpoint fetches the canonical regime and recommended allocation
    server-side and returns a full alignment verdict including score,
    deviations, range compliance, and suggested adjustments.
    """
    weights = body.to_weights()
    service = AlignmentService()

    try:
        return await service.compute_alignment(
            tenant_id=tenant_id,
            portfolio=weights,
            session=session,
            objective=body.objective,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/alignment/sample", response_model=AlignmentResponse)
async def get_portfolio_alignment_sample(
    tenant_id: UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Return an alignment verdict for a default 60/30/10 portfolio.

    Useful for:
      - frontend empty states (no real portfolio on file yet),
      - smoke-testing the alignment pipeline,
      - showcasing the feature.
    """
    sample = PortfolioWeights(equity=0.60, bonds=0.30, cash=0.10)
    service = AlignmentService()

    try:
        return await service.compute_alignment(
            tenant_id=tenant_id,
            portfolio=sample,
            session=session,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/health")
async def portfolio_health_check():
    """Health check for the portfolio alignment service."""
    return {
        "status": "healthy",
        "service": "portfolio_alignment",
        "engine": "grine_regime_engine v0.3.0",
    }

"""Portfolio alignment service.

Orchestration shell. Fetches canonical regime + recommendation from the
existing services, runs the pure scoring functions from
`alignment_scoring`, and assembles the response. No engine calls here,
no numerical logic here — this file is plumbing only.

The rule: if you need to change how the score is computed, edit
`alignment_scoring.py`. If you need to change how the data flows, edit
this file.
"""
from __future__ import annotations

import time
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.portfolio import (
    AlignmentDetail,
    AlignmentRegimeContext,
    AlignmentResponse,
    PortfolioWeights,
    RecommendedContext,
)
from app.services.alignment_scoring import (
    ASSETS,
    compute_deviations,
    compute_range_status,
    compute_score,
    confidence_label,
    resolve_inputs,
    suggest_adjustments,
)
from app.services.allocation_service import AllocationService
from app.services.regime_service import RegimeService


class AlignmentService:
    """Computes portfolio alignment against the canonical Grine doctrine."""

    def __init__(self) -> None:
        self.regime_service = RegimeService()
        self.allocation_service = AllocationService()

    async def compute_alignment(
        self,
        tenant_id: UUID,
        portfolio: PortfolioWeights,
        session: AsyncSession,
        objective: str | None = None,
    ) -> AlignmentResponse:
        """Compute a full alignment verdict for the tenant's portfolio."""
        start = time.time()

        # Pull canonical regime + recommendation. No engine calls here.
        regime = await self.regime_service.get_current_regime(
            tenant_id, session, force_refresh=False
        )
        if regime is None:
            raise ValueError(
                "Unable to determine current regime for tenant."
            )

        recommendation = await self.allocation_service.get_recommended_allocation(
            tenant_id=tenant_id,
            session=session,
            force_refresh=False,
            objective=objective,
        )
        if recommendation is None:
            raise ValueError(
                "Unable to determine recommended allocation for tenant."
            )

        # Pure scoring.
        inputs = resolve_inputs(portfolio, regime, recommendation)
        deviations = compute_deviations(inputs)
        range_status = compute_range_status(inputs)
        score, label, breakdown = compute_score(deviations, range_status)
        adjustments = suggest_adjustments(deviations)

        processing_ms = (time.time() - start) * 1000.0

        return AlignmentResponse(
            regime=AlignmentRegimeContext(
                state=regime.final_state,
                confidence=confidence_label(regime.confidence),
                confidence_value=regime.confidence,
            ),
            portfolio={
                "equity": inputs.portfolio.equity,
                "bonds": inputs.portfolio.bonds,
                "cash": inputs.portfolio.cash,
            },
            recommended=RecommendedContext(
                target=inputs.target,
                ranges={
                    a: [inputs.ranges[a][0], inputs.ranges[a][1]]
                    for a in ASSETS
                },
            ),
            alignment=AlignmentDetail(
                score=score,
                label=label,
                deviations=deviations,
                range_status=range_status,
                penalty_breakdown=breakdown,
            ),
            suggested_adjustments=adjustments,
            tenant_id=tenant_id,
            regime_detection_id=regime.id,
            recommendation_id=recommendation.id,
            processing_time_ms=round(processing_ms, 2),
        )

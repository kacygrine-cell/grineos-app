"""Portfolio alignment schemas."""
from __future__ import annotations

from typing import Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


RangeStatus = Literal["below", "inside", "above"]
AlignmentLabel = Literal["Highly Aligned", "Moderately Aligned", "Misaligned"]
ConfidenceLabel = Literal["HIGH", "MODERATE", "LOW"]


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class PortfolioWeights(BaseModel):
    """Input portfolio weights. Must cover equity/bonds/cash."""
    equity: float = Field(ge=0, le=1)
    bonds: float = Field(ge=0, le=1)
    cash: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def _check_sum(self) -> "PortfolioWeights":
        total = self.equity + self.bonds + self.cash
        if total <= 0:
            raise ValueError("Weights must sum to more than zero.")
        # Allow up to 2% drift from 1.0; we normalize internally.
        if abs(total - 1.0) > 0.02:
            raise ValueError(
                f"Weights should sum to ~1.0 (got {total:.3f}). "
                f"Provide proportions, not percentages."
            )
        return self

    def normalized(self) -> "PortfolioWeights":
        """Return self, rescaled so weights sum to exactly 1.0."""
        total = self.equity + self.bonds + self.cash
        return PortfolioWeights(
            equity=self.equity / total,
            bonds=self.bonds / total,
            cash=self.cash / total,
        )


class AlignmentRequest(BaseModel):
    """Request body for POST /portfolio/alignment."""
    # Required: asset-class weights
    equity: float = Field(ge=0, le=1)
    bonds: float = Field(ge=0, le=1)
    cash: float = Field(ge=0, le=1)

    # Optional context
    dividend_equity_share: Optional[float] = Field(
        default=None, ge=0, le=1,
        description="Share of equity allocated to dividend strategies (0-1).",
    )
    portfolio_id: Optional[str] = Field(
        default=None, description="Client-side portfolio identifier (opaque).",
    )

    # Optional optimizer override (pass-through to allocation engine)
    objective: Optional[str] = Field(
        default=None,
        description="Optimizer objective override: min_variance | max_sharpe | risk_parity",
    )

    def to_weights(self) -> PortfolioWeights:
        return PortfolioWeights(
            equity=self.equity, bonds=self.bonds, cash=self.cash
        ).normalized()


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class AlignmentRegimeContext(BaseModel):
    """Regime context embedded in the alignment response."""
    state: str = Field(description="Strategic regime state, e.g. EXPANSION")
    confidence: ConfidenceLabel
    confidence_value: float = Field(ge=0, le=1)


class RecommendedContext(BaseModel):
    """Recommended allocation snapshot used for the comparison."""
    target: Dict[str, float]                      # equity/bonds/cash target
    ranges: Dict[str, List[float]]                # equity: [lower, upper]


class AlignmentDetail(BaseModel):
    """The alignment verdict."""
    score: int = Field(ge=0, le=100)
    label: AlignmentLabel
    deviations: Dict[str, float]                  # user - target per sleeve
    range_status: Dict[str, RangeStatus]
    penalty_breakdown: Dict[str, float] = Field(
        default_factory=dict,
        description="Transparency into the scoring — penalty per sleeve."
    )


class AlignmentResponse(BaseModel):
    """Full alignment response."""
    regime: AlignmentRegimeContext
    portfolio: Dict[str, float]
    recommended: RecommendedContext
    alignment: AlignmentDetail
    suggested_adjustments: List[str]

    # Metadata
    tenant_id: UUID
    regime_detection_id: Optional[UUID] = None
    recommendation_id: Optional[UUID] = None
    processing_time_ms: Optional[float] = None

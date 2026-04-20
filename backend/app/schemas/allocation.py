"""Allocation API response schemas."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class AllocationWeights(BaseModel):
    """Portfolio allocation weights."""
    equity: float = Field(ge=0, le=1, description="Equity allocation (0-1)")
    bonds: float = Field(ge=0, le=1, description="Bonds allocation (0-1)")
    cash: float = Field(ge=0, le=1, description="Cash allocation (0-1)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "equity": 0.65,
                "bonds": 0.28,
                "cash": 0.07
            }
        }


class AllocationRanges(BaseModel):
    """Constraint ranges for each asset class."""
    equity: Dict[str, float] = Field(description="Equity min/max range")
    bonds: Dict[str, float] = Field(description="Bonds min/max range") 
    cash: Dict[str, float] = Field(description="Cash min/max range")
    
    class Config:
        json_schema_extra = {
            "example": {
                "equity": {"lower": 0.60, "upper": 0.70},
                "bonds": {"lower": 0.20, "upper": 0.30},
                "cash": {"lower": 0.00, "upper": 0.05}
            }
        }


class TurnoverInfo(BaseModel):
    """Turnover analysis."""
    realized: float = Field(ge=0, description="Realized L1 turnover")
    proposed: float = Field(ge=0, description="Proposed turnover (before cap)")
    cap: float = Field(ge=0, description="Turnover cap applied")
    capped: bool = Field(description="Whether cap was binding")
    
    class Config:
        json_schema_extra = {
            "example": {
                "realized": 0.12,
                "proposed": 0.25,
                "cap": 0.15,
                "capped": True
            }
        }


class DividendSplit(BaseModel):
    """Dividend/growth split within equity."""
    equity_total: float = Field(ge=0, le=1, description="Total equity weight")
    growth: float = Field(ge=0, le=1, description="Growth equity weight")
    dividend: float = Field(ge=0, le=1, description="Dividend equity weight")
    dividend_share: float = Field(ge=0, le=1, description="Dividend as % of equity")
    range_lower: float = Field(ge=0, le=1, description="Min dividend share for regime")
    range_upper: float = Field(ge=0, le=1, description="Max dividend share for regime")
    
    class Config:
        json_schema_extra = {
            "example": {
                "equity_total": 0.65,
                "growth": 0.553,
                "dividend": 0.097,
                "dividend_share": 0.15,
                "range_lower": 0.0,
                "range_upper": 0.2
            }
        }


class AllocationConstraints(BaseModel):
    """Allocation constraints and parameters."""
    regime_state: str = Field(description="Strategic regime state")
    ranges: AllocationRanges
    turnover_cap: float = Field(description="L1 turnover cap")
    objective: str = Field(description="Optimizer objective used")
    optimizer_status: str = Field(description="Optimizer convergence status")


class AllocationResponse(BaseModel):
    """Recommended allocation response."""
    # Core allocation
    final_weights: AllocationWeights = Field(description="Final recommended weights")
    target_weights: AllocationWeights = Field(description="Target weights before turnover cap")
    
    # Constraints and parameters  
    constraints: AllocationConstraints
    
    # Analysis
    turnover: TurnoverInfo
    dividend_split: DividendSplit
    
    # Change analysis
    change_reason: Optional[str] = Field(description="Why the allocation changed")
    change_magnitude: Optional[str] = Field(description="Change magnitude: minor/moderate/major")
    
    # Metadata
    recommendation_id: UUID
    regime_detection_id: UUID
    tenant_id: UUID
    created_at: datetime
    processing_time_ms: Optional[float]
    
    class Config:
        json_schema_extra = {
            "example": {
                "final_weights": {"equity": 0.65, "bonds": 0.28, "cash": 0.07},
                "target_weights": {"equity": 0.70, "bonds": 0.25, "cash": 0.05},
                "constraints": {
                    "regime_state": "EXPANSION",
                    "ranges": {
                        "equity": {"lower": 0.60, "upper": 0.70},
                        "bonds": {"lower": 0.20, "upper": 0.30},
                        "cash": {"lower": 0.00, "upper": 0.05}
                    },
                    "turnover_cap": 0.15,
                    "objective": "min_variance",
                    "optimizer_status": "optimal"
                },
                "turnover": {
                    "realized": 0.12,
                    "proposed": 0.25,
                    "cap": 0.15,
                    "capped": True
                },
                "dividend_split": {
                    "equity_total": 0.65,
                    "growth": 0.553,
                    "dividend": 0.097,
                    "dividend_share": 0.15,
                    "range_lower": 0.0,
                    "range_upper": 0.2
                },
                "change_reason": "Regime shifted from BALANCED to EXPANSION with high confidence",
                "change_magnitude": "moderate"
            }
        }


class AllocationHistoryItem(BaseModel):
    """Single allocation history entry."""
    recommendation_id: UUID
    weights: AllocationWeights
    regime_state: str
    confidence: float
    momentum: float
    turnover: float
    change_magnitude: Optional[str]
    created_at: datetime


class AllocationHistoryResponse(BaseModel):
    """Allocation history response."""
    current: AllocationResponse
    history: List[AllocationHistoryItem]
    total_count: int
    date_range: Dict[str, datetime]
    
    # Aggregate statistics
    stats: Dict[str, Any] = Field(
        description="Historical statistics",
        default_factory=lambda: {
            "avg_turnover": 0.0,
            "regime_distribution": {},
            "rebalance_frequency": 0.0
        }
    )

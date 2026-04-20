"""Regime API response schemas."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class RegimeProbabilities(BaseModel):
    """Regime probability distribution."""
    bull: float = Field(ge=0, le=1)
    bear: float = Field(ge=0, le=1)
    crisis: float = Field(ge=0, le=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "bull": 0.65,
                "bear": 0.30,
                "crisis": 0.05
            }
        }


class RegimeMetadata(BaseModel):
    """Regime detection metadata."""
    detector_type: str
    n_regimes: int
    data_start_date: Optional[datetime]
    data_end_date: Optional[datetime]
    data_points: Optional[int]
    processing_time_ms: Optional[float]
    cache_hit: bool = False


class RegimeResponse(BaseModel):
    """Current regime detection response."""
    # Core regime data
    final_state: str = Field(
        description="Strategic regime state",
        examples=["EXPANSION", "BALANCED", "TRANSITION", "ENDURANCE", "PROTECTION"]
    )
    raw_regime: Optional[str] = Field(
        description="Raw detected regime label",
        examples=["bull", "bear", "crisis", "recovery", "chop"]
    )
    confidence: float = Field(
        ge=0, le=1,
        description="Regime confidence score (0-1)"
    )
    momentum: float = Field(
        ge=-1, le=1,
        description="Market momentum signal (-1 to +1)"
    )
    
    # Probabilities
    probabilities: Optional[RegimeProbabilities] = Field(
        description="Regime probability distribution"
    )
    
    # Metadata
    metadata: RegimeMetadata
    detection_id: UUID
    tenant_id: UUID
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "final_state": "EXPANSION",
                "raw_regime": "bull", 
                "confidence": 0.75,
                "momentum": 0.35,
                "probabilities": {
                    "bull": 0.75,
                    "bear": 0.20,
                    "crisis": 0.05
                },
                "metadata": {
                    "detector_type": "GaussianHMM",
                    "n_regimes": 3,
                    "data_points": 252,
                    "processing_time_ms": 145.2,
                    "cache_hit": False
                }
            }
        }


class RegimeTransitionResponse(BaseModel):
    """Regime transition information."""
    from_state: str
    to_state: str
    confidence_change: float
    momentum_change: float
    trigger_event: Optional[str]
    transition_date: datetime
    
    
class RegimeHistoryResponse(BaseModel):
    """Historical regime data."""
    detections: List[RegimeResponse]
    transitions: List[RegimeTransitionResponse]
    total_count: int
    date_range: Dict[str, datetime]

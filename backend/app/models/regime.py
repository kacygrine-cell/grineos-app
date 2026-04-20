"""Regime detection models with tenant isolation."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Float, Integer, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class RegimeDetection(Base):
    """Regime detection results with full audit trail."""
    __tablename__ = "regime_detections"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    
    # Core regime data
    final_state: Mapped[str] = mapped_column(String(50))  # EXPANSION, BALANCED, etc.
    raw_regime: Mapped[Optional[str]] = mapped_column(String(50))  # bull, bear, crisis, etc.
    confidence: Mapped[float] = mapped_column(Float)
    momentum: Mapped[float] = mapped_column(Float)
    
    # Probabilities as JSON array
    probabilities: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Engine metadata
    detector_type: Mapped[str] = mapped_column(String(100), default="GaussianHMM")
    n_regimes: Mapped[int] = mapped_column(Integer, default=3)
    data_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    data_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    data_points: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Performance metrics
    processing_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    cache_hit: Mapped[bool] = mapped_column(default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    

class RegimeTransition(Base):
    """Regime transition events for analysis."""
    __tablename__ = "regime_transitions"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    
    from_state: Mapped[str] = mapped_column(String(50))
    to_state: Mapped[str] = mapped_column(String(50))
    
    # Transition characteristics
    confidence_change: Mapped[float] = mapped_column(Float)
    momentum_change: Mapped[float] = mapped_column(Float)
    trigger_event: Mapped[Optional[str]] = mapped_column(String(200))
    
    # References to the detection records
    from_detection_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("regime_detections.id"))
    to_detection_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("regime_detections.id"))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class MarketData(Base):
    """Market data cache for regime detection."""
    __tablename__ = "market_data"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    
    # OHLCV data
    open_price: Mapped[float] = mapped_column(Float)
    high_price: Mapped[float] = mapped_column(Float)
    low_price: Mapped[float] = mapped_column(Float)
    close_price: Mapped[float] = mapped_column(Float)
    volume: Mapped[Optional[float]] = mapped_column(Float)
    
    # Derived data
    returns: Mapped[Optional[float]] = mapped_column(Float)
    log_returns: Mapped[Optional[float]] = mapped_column(Float)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        # Unique constraint on tenant + symbol + date
        {"schema": None},
    )

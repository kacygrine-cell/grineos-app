"""Allocation engine models with tenant isolation."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Float, Boolean, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AllocationRecommendation(Base):
    """Allocation engine recommendations with full audit trail."""
    __tablename__ = "allocation_recommendations"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    
    # Link to regime detection
    regime_detection_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("regime_detections.id"))
    
    # Final allocation weights
    equity_weight: Mapped[float] = mapped_column(Float)
    bonds_weight: Mapped[float] = mapped_column(Float)
    cash_weight: Mapped[float] = mapped_column(Float)
    
    # Target weights (before turnover cap)
    target_equity: Mapped[float] = mapped_column(Float)
    target_bonds: Mapped[float] = mapped_column(Float)
    target_cash: Mapped[float] = mapped_column(Float)
    
    # Previous weights (for turnover calculation)
    previous_equity: Mapped[Optional[float]] = mapped_column(Float)
    previous_bonds: Mapped[Optional[float]] = mapped_column(Float)
    previous_cash: Mapped[Optional[float]] = mapped_column(Float)
    
    # Constraint bands as JSON
    constraints: Mapped[dict] = mapped_column(JSON)
    
    # Turnover data
    turnover_realized: Mapped[float] = mapped_column(Float)
    turnover_proposed: Mapped[float] = mapped_column(Float)
    turnover_capped: Mapped[bool] = mapped_column(Boolean)
    turnover_cap: Mapped[float] = mapped_column(Float, default=0.15)
    
    # Dividend split
    dividend_growth_weight: Mapped[float] = mapped_column(Float)
    dividend_income_weight: Mapped[float] = mapped_column(Float)
    dividend_share: Mapped[float] = mapped_column(Float)
    dividend_range_lower: Mapped[float] = mapped_column(Float)
    dividend_range_upper: Mapped[float] = mapped_column(Float)
    
    # Engine parameters
    optimizer_objective: Mapped[str] = mapped_column(String(50), default="min_variance")
    optimizer_status: Mapped[str] = mapped_column(String(50))
    momentum_weight: Mapped[float] = mapped_column(Float, default=0.25)
    tracking_weight: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Performance metadata
    processing_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Change explanation
    change_reason: Mapped[Optional[str]] = mapped_column(Text)
    change_magnitude: Mapped[Optional[str]] = mapped_column(String(20))  # "minor", "moderate", "major"
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class PortfolioState(Base):
    """Current portfolio state per tenant."""
    __tablename__ = "portfolio_states"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), unique=True, index=True)
    
    # Current holdings
    current_equity: Mapped[float] = mapped_column(Float)
    current_bonds: Mapped[float] = mapped_column(Float)
    current_cash: Mapped[float] = mapped_column(Float)
    
    # Last allocation recommendation
    last_recommendation_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("allocation_recommendations.id")
    )
    
    # Portfolio metadata
    total_value: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    last_rebalanced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Performance tracking
    inception_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ytd_return: Mapped[Optional[float]] = mapped_column(Float)
    total_return: Mapped[Optional[float]] = mapped_column(Float)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AllocationChange(Base):
    """Track significant allocation changes for audit and explanation."""
    __tablename__ = "allocation_changes"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    
    # References
    from_recommendation_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("allocation_recommendations.id")
    )
    to_recommendation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("allocation_recommendations.id")
    )
    
    # Change details
    equity_change: Mapped[float] = mapped_column(Float)
    bonds_change: Mapped[float] = mapped_column(Float)
    cash_change: Mapped[float] = mapped_column(Float)
    total_change: Mapped[float] = mapped_column(Float)  # L1 norm
    
    # Classification
    change_type: Mapped[str] = mapped_column(String(50))  # "regime_shift", "confidence_change", "momentum_shift"
    change_magnitude: Mapped[str] = mapped_column(String(20))  # "minor", "moderate", "major"
    
    # AI-generated explanation
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

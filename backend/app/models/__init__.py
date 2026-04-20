"""Models package - imports all models for SQLAlchemy registration."""

# Import all models so they're registered with SQLAlchemy Base
from .user import User, Tenant
from .regime import RegimeDetection, RegimeTransition, MarketData
from .allocation import AllocationRecommendation, PortfolioState, AllocationChange

__all__ = [
    "User",
    "Tenant", 
    "RegimeDetection",
    "RegimeTransition",
    "MarketData",
    "AllocationRecommendation",
    "PortfolioState",
    "AllocationChange"
]

"""Main v1 API router."""
from fastapi import APIRouter

from app.api.v1 import allocation, portfolio, regime

router = APIRouter()

# Include all v1 routers
router.include_router(regime.router, prefix="/regime", tags=["Regime"])
router.include_router(allocation.router, prefix="/allocation", tags=["Allocation"])
router.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])

"""API dependencies for authentication and tenant isolation."""
from typing import Optional
from uuid import UUID

from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.user import User, Tenant


async def get_current_tenant_id(
    x_tenant_id: Optional[str] = Header(None, description="Tenant ID header"),
    authorization: Optional[str] = Header(None, description="Bearer token")
) -> UUID:
    """
    Extract tenant ID from request headers.
    
    In production, this would validate JWT tokens and extract tenant from claims.
    For demo purposes, we accept tenant ID directly via header.
    """
    if x_tenant_id:
        try:
            return UUID(x_tenant_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid tenant ID format"
            )
    
    # In production: decode JWT from Authorization header and extract tenant_id
    if authorization and authorization.startswith("Bearer "):
        # JWT token validation would happen here
        # For demo, we'll create a default tenant
        from uuid import uuid4
        return uuid4()  # Would be extracted from validated JWT claims
    
    raise HTTPException(
        status_code=401,
        detail="Authentication required. Provide X-Tenant-ID header or Bearer token."
    )


async def get_current_user(
    tenant_id: UUID = Depends(get_current_tenant_id),
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session)
) -> Optional[User]:
    """
    Get current authenticated user.
    
    In production, this would decode and validate the JWT token.
    """
    # For demo purposes, return None - authentication is simplified
    # In production: decode JWT, validate signature, extract user_id, query database
    return None


async def verify_tenant_access(
    tenant_id: UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session)
) -> Tenant:
    """
    Verify tenant exists and is active.
    
    This ensures tenant isolation - users can only access their tenant's data.
    """
    from sqlalchemy.future import select
    
    stmt = select(Tenant).where(
        Tenant.id == tenant_id,
        Tenant.is_active == True
    )
    
    result = await session.execute(stmt)
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        # For demo purposes, create a default tenant if none exists
        tenant = Tenant(
            id=tenant_id,
            name="Demo Tenant",
            slug="demo-tenant",
            plan="demo",
            max_allocations_per_day=1000,
            default_turnover_cap=0.15,
            default_optimizer="min_variance",
            is_active=True
        )
        session.add(tenant)
        await session.commit()
        await session.refresh(tenant)
    
    return tenant


# Rate limiting dependency (simplified for demo)
async def check_rate_limits(
    tenant_id: UUID = Depends(get_current_tenant_id),
    tenant: Tenant = Depends(verify_tenant_access)
) -> bool:
    """
    Check if tenant is within rate limits for API calls.
    
    In production, this would check Redis for rate limit counters.
    """
    # For demo purposes, always allow
    # In production: check Redis counters against tenant.max_allocations_per_day
    return True

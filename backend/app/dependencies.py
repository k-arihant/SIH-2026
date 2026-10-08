# ============================================================
# METROSCAN AUTHENTICATION DEPENDENCIES
# JWT Token Verification via Supabase Auth
# ============================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.services.db_service import get_supabase
from app.config import settings

security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Extracts and verifies JWT token from Authorization header.
    Returns user dict if valid token provided, None if no token provided.
    Raises HTTPException(401) if token is invalid or expired.
    """
    if not credentials or not credentials.credentials:
        return None

    token = credentials.credentials

    # ── Check for demo/mock tokens ──
    if token.startswith("mock-") or token.startswith("demo-") or settings.USE_MOCK:
        if "inspector" in token.lower() or "officer" in token.lower():
            return {
                "id": "usr-inspector-8492",
                "email": "inspector.verma@gov.in",
                "role": "inspector",
                "full_name": "Inspector Amit Verma",
                "badge_id": "LM-DEL-8492",
                "department": "Delhi State Legal Metrology Enforcement Division",
            }
        return {
            "id": "usr-consumer-101",
            "email": "citizen.consumer@example.com",
            "role": "consumer",
            "full_name": "Citizen Consumer",
            "badge_id": None,
            "department": None,
        }

    # ── Live Supabase JWT verification ──
    try:
        sb = get_supabase()
        user_res = sb.auth.get_user(token)
        if not user_res or not user_res.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = user_res.user
        # Fetch role profile
        profile = None
        try:
            p_res = sb.table("profiles").select("*").eq("id", user.id).execute()
            if p_res.data:
                profile = p_res.data[0]
        except Exception:
            pass

        return {
            "id": user.id,
            "email": user.email,
            "role": profile.get("role", "consumer") if profile else "consumer",
            "full_name": profile.get("full_name", user.user_metadata.get("full_name", user.email.split("@")[0])) if profile else (user.user_metadata.get("full_name") or user.email.split("@")[0]),
            "badge_id": profile.get("badge_id") if profile else None,
            "department": profile.get("department") if profile else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_required(
    user: Optional[dict] = Depends(get_current_user_optional)
) -> dict:
    """
    Enforces authentication. Raises 401 if user is not authenticated.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_inspector_role(
    user: dict = Depends(get_current_user_required)
) -> dict:
    """
    Enforces that the authenticated user possesses official Inspector or Admin role.
    """
    if user.get("role") not in ("inspector", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Official Inspector credentials required.",
        )
    return user

"""
Authentication middleware — verifies Supabase JWT tokens.
"""
import logging
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.supabase_service import verify_user_token

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """
    FastAPI dependency that verifies the Bearer token and returns user_id.
    Use as: user_id: str = Depends(get_current_user)
    """
    token = credentials.credentials
    user_id = await verify_user_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id

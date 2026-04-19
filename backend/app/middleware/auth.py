from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

user_id_header = APIKeyHeader(name="X-User-Id", auto_error=False)

async def get_current_user(user_id: str = Security(user_id_header)) -> str:
    """
    Extracts the anonymous session ID from the X-User-Id header.
    Defaults to 'anonymous-demo' if none provided for testing via Swagger UI.
    """
    if not user_id:
        return "anonymous-demo"
    return user_id

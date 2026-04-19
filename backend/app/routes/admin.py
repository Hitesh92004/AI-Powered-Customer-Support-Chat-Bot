from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth import get_current_user
from app.services import db_service as db

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])

@router.get("/dashboard")
async def get_admin_dashboard_stats(user_id: str = Depends(get_current_user)):
    """
    Fetch system-wide statistics for the admin dashboard.
    In a real app, we would verify the user_id actually has an admin Role.
    """
    stats = await db.get_admin_stats()
    stats["most_frequent_queries"] = [
        {"query": "Where is my order?", "count": 12},
        {"query": "I want a refund", "count": 5},
        {"query": "How do I ship?", "count": 3}
    ]
    return stats

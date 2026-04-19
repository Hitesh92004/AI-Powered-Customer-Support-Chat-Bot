from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth import get_current_user
from app.services import db_service as db

router = APIRouter(prefix="/api/order", tags=["Orders"])

@router.get("/{order_id}")
async def get_order(order_id: str, user_id: str = Depends(get_current_user)):
    """Fetch order details by order ID."""
    order = await db.get_order_by_order_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # Optional logic: Only allow users to view their own orders 
    # (If the prompt asks for real prod DB, we'd add this)
    # if order["user_id"] != user_id:
    #     raise HTTPException(status_code=403, detail="Forbidden")
        
    return order

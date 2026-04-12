"""
Conversations routes — CRUD for conversations and messages.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth import get_current_user
from app.models.schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
    ConversationMessagesResponse,
    MessageResponse,
)
from app.services import supabase_service as db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


@router.get("", response_model=ConversationListResponse)
async def list_conversations(user_id: str = Depends(get_current_user)):
    """List all conversations for the current user."""
    conversations = await db.get_conversations(user_id)

    conv_list = []
    for c in conversations:
        # Extract message count from joined query
        msg_count = 0
        if "messages" in c and c["messages"]:
            msg_count = c["messages"][0].get("count", 0) if isinstance(c["messages"], list) else 0

        conv_list.append(ConversationResponse(
            id=c["id"],
            title=c["title"],
            created_at=c["created_at"],
            updated_at=c["updated_at"],
            message_count=msg_count,
        ))

    return ConversationListResponse(conversations=conv_list, total=len(conv_list))


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    body: ConversationCreate,
    user_id: str = Depends(get_current_user),
):
    """Create a new conversation."""
    conversation = await db.create_conversation(user_id, body.title)
    return ConversationResponse(
        id=conversation["id"],
        title=conversation["title"],
        created_at=conversation["created_at"],
        updated_at=conversation["updated_at"],
    )


@router.get("/{conversation_id}", response_model=ConversationMessagesResponse)
async def get_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user),
):
    """Get a conversation and all its messages."""
    conversation = await db.get_conversation_by_id(conversation_id, user_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    messages = await db.get_messages(conversation_id)
    message_list = [
        MessageResponse(
            id=m["id"],
            conversation_id=m["conversation_id"],
            role=m["role"],
            content=m["content"],
            created_at=m["created_at"],
        )
        for m in messages
    ]

    return ConversationMessagesResponse(
        conversation_id=conversation_id,
        title=conversation["title"],
        messages=message_list,
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user),
):
    """Delete a conversation and all its messages."""
    conversation = await db.get_conversation_by_id(conversation_id, user_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    await db.delete_conversation(conversation_id, user_id)

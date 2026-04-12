"""
Conversations routes — CRUD using Neon db_service.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.middleware.auth import get_current_user
from app.models.schemas import (
    ConversationCreate, ConversationResponse, ConversationListResponse,
    ConversationMessagesResponse, MessageResponse,
)
from app.services import db_service as db

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


@router.get("", response_model=ConversationListResponse)
async def list_conversations(user_id: str = Depends(get_current_user)):
    conversations = await db.get_conversations(user_id)
    conv_list = [
        ConversationResponse(
            id=str(c["id"]),
            title=c["title"],
            created_at=c["created_at"],
            updated_at=c["updated_at"],
            message_count=int(c.get("message_count", 0)),
        )
        for c in conversations
    ]
    return ConversationListResponse(conversations=conv_list, total=len(conv_list))


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(body: ConversationCreate, user_id: str = Depends(get_current_user)):
    c = await db.create_conversation(user_id, body.title)
    return ConversationResponse(
        id=str(c["id"]), title=c["title"],
        created_at=c["created_at"], updated_at=c["updated_at"],
    )


@router.get("/{conversation_id}", response_model=ConversationMessagesResponse)
async def get_conversation(conversation_id: str, user_id: str = Depends(get_current_user)):
    conversation = await db.get_conversation_by_id(conversation_id, user_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    messages = await db.get_messages(conversation_id)
    return ConversationMessagesResponse(
        conversation_id=conversation_id,
        title=conversation["title"],
        messages=[
            MessageResponse(
                id=str(m["id"]), conversation_id=str(m["conversation_id"]),
                role=m["role"], content=m["content"], created_at=m["created_at"],
            ) for m in messages
        ],
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: str, user_id: str = Depends(get_current_user)):
    conversation = await db.get_conversation_by_id(conversation_id, user_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    await db.delete_conversation(conversation_id, user_id)

"""
Pydantic models/schemas for request and response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─── Chat Schemas ─────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = None
    document_context: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    user_message_id: Optional[str] = None
    assistant_message_id: Optional[str] = None


# ─── Conversation Schemas ─────────────────────────────────────────────────────

class ConversationCreate(BaseModel):
    title: str = Field(default="New Conversation", max_length=255)


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0


class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int


# ─── Message Schemas ──────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime


class ConversationMessagesResponse(BaseModel):
    conversation_id: str
    title: str
    messages: List[MessageResponse]


# ─── Document Schemas ─────────────────────────────────────────────────────────

class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    content_preview: str
    char_count: int
    conversation_id: Optional[str] = None
    message: str = "Document processed successfully"


# ─── FAQ & Handoff Schemas ───────────────────────────────────────────────────

class FAQTrainResponse(BaseModel):
    source_filename: str
    inserted: int
    skipped: int
    message: str


class HandoffTicketResponse(BaseModel):
    id: str
    conversation_id: str
    reason: str
    status: str
    created_at: datetime


# ─── Health ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    groq_configured: bool
    db_connected: bool

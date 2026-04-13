"""
Chat routes — POST /api/chat with streaming support.
"""
import logging
import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.middleware.auth import get_current_user
from app.models.schemas import ChatRequest, ChatResponse
from app.services import gemini_service, groq_service
from app.services import db_service as db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])


def _is_quota_error(error: RuntimeError) -> bool:
    message = str(error).lower()
    return "usage limits" in message or "quota" in message or "429" in message


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, user_id: str = Depends(get_current_user)):
    """Send a message and get a full AI response."""
    # Get or create conversation
    if request.conversation_id:
        conversation = await db.get_conversation_by_id(request.conversation_id, user_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found.")
        conversation_id = request.conversation_id
    else:
        title = request.message[:60] + ("..." if len(request.message) > 60 else "")
        conversation = await db.create_conversation(user_id, title)
        conversation_id = str(conversation["id"])

    # Fetch history for context
    history = await db.get_messages(conversation_id)
    history_dicts = [{"role": m["role"], "content": m["content"]} for m in history]

    # Save user message
    user_msg = await db.save_message(conversation_id, "user", request.message)

    # Get AI response
    try:
        ai_response = await gemini_service.gemini_service.chat(
            user_message=request.message,
            history=history_dicts,
            document_context=request.document_context,
        )
    except RuntimeError as e:
        if _is_quota_error(e):
            logger.warning("Gemini quota hit in chat endpoint, falling back to Groq.")
            try:
                ai_response = await groq_service.groq_service.chat(
                    user_message=request.message,
                    history=history_dicts,
                    document_context=request.document_context,
                )
            except RuntimeError as groq_error:
                raise HTTPException(status_code=503, detail=str(groq_error))
        else:
            raise HTTPException(status_code=503, detail=str(e))

    # Save assistant message
    assistant_msg = await db.save_message(conversation_id, "assistant", ai_response)

    return ChatResponse(
        response=ai_response,
        conversation_id=conversation_id,
        user_message_id=str(user_msg["id"]),
        assistant_message_id=str(assistant_msg["id"]),
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest, user_id: str = Depends(get_current_user)):
    """Stream an AI response using Server-Sent Events."""
    if request.conversation_id:
        conversation = await db.get_conversation_by_id(request.conversation_id, user_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found.")
        conversation_id = request.conversation_id
    else:
        title = request.message[:60] + ("..." if len(request.message) > 60 else "")
        conversation = await db.create_conversation(user_id, title)
        conversation_id = str(conversation["id"])

    history = await db.get_messages(conversation_id)
    history_dicts = [{"role": m["role"], "content": m["content"]} for m in history]
    await db.save_message(conversation_id, "user", request.message)

    async def generate():
        full_response = ""
        yield f"data: {json.dumps({'type': 'meta', 'conversation_id': conversation_id})}\n\n"
        try:
            async for chunk in gemini_service.gemini_service.stream_chat(
                user_message=request.message,
                history=history_dicts,
                document_context=request.document_context,
            ):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        except RuntimeError as e:
            if not _is_quota_error(e):
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                return

            logger.warning("Gemini quota hit in streaming endpoint, falling back to Groq.")
            try:
                async for chunk in groq_service.groq_service.stream_chat(
                    user_message=request.message,
                    history=history_dicts,
                    document_context=request.document_context,
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            except RuntimeError as groq_error:
                yield f"data: {json.dumps({'type': 'error', 'message': str(groq_error)})}\n\n"
                return

        await db.save_message(conversation_id, "assistant", full_response)
        yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

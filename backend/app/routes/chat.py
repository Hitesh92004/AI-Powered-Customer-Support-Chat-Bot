"""
Chat routes — POST /api/chat with streaming support.
"""
import logging
import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.middleware.auth import get_current_user
from app.models.schemas import ChatRequest, ChatResponse
from app.config import settings
from app.services import groq_service
from app.services.faq_service import load_faq_entries_from_dataset
from app.services.intent_service import intent_router_service
from app.services import db_service as db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])


def _build_faq_context(faq_matches: list[dict]) -> str:
    parts = []
    for idx, item in enumerate(faq_matches, start=1):
        parts.append(f"FAQ #{idx}\nQ: {item['question']}\nA: {item['answer']}")
    return "\n\n".join(parts)


async def _ensure_user_faq_seeded(user_id: str) -> None:
    """
    Ensure user has FAQ entries seeded from server dataset.
    Always attempts to seed any missing entries (idempotent — skips duplicates).
    """
    try:
        entries = load_faq_entries_from_dataset(settings.FAQ_DATASET_PATH)
    except Exception as e:
        logger.warning("FAQ auto-seed skipped for user %s: %s", user_id, e)
        return

    source_name = settings.FAQ_DATASET_PATH.split("/")[-1]
    inserted = 0
    for entry in entries:
        if await db.faq_entry_exists(user_id=user_id, question=entry["question"]):
            continue
        await db.save_faq_entry(
            user_id=user_id,
            question=entry["question"],
            answer=entry["answer"],
            source_document=source_name,
        )
        inserted += 1

    if inserted:
        logger.info("Auto-seeded %s FAQ entries for user %s", inserted, user_id)


async def _intent_handoff_message(
    user_id: str,
    conversation_id: str,
    user_message: str,
) -> str | None:
    """
    Use sklearn intent classifier to trigger human handoff when confidence is high
    for 'human' escalation intent.
    """
    prediction = intent_router_service.predict(user_message)
    if not prediction:
        return None

    label = (prediction.get("label") or "").strip().lower()
    confidence = float(prediction.get("confidence") or 0.0)
    if label != "human" or confidence < settings.INTENT_CONFIDENCE_THRESHOLD:
        return None

    ticket = await db.create_handoff_ticket(
        user_id=user_id,
        conversation_id=conversation_id,
        user_message=user_message,
        reason=f"Intent router escalation (label={label}, confidence={confidence:.3f})",
    )
    return (
        "I understood that you'd like to talk to a human support agent. "
        f"I've escalated your request (ticket: {str(ticket['id'])[:8]})."
    )


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

    # Check for human handoff intent first
    intent_handoff = await _intent_handoff_message(user_id, conversation_id, request.message)
    if intent_handoff:
        assistant_msg = await db.save_message(conversation_id, "assistant", intent_handoff)
        return ChatResponse(
            response=intent_handoff,
            conversation_id=conversation_id,
            user_message_id=str(user_msg["id"]),
            assistant_message_id=str(assistant_msg["id"]),
        )

    # Seed FAQ data for this user if missing, then search
    await _ensure_user_faq_seeded(user_id)
    faq_matches = await db.search_faq_entries(user_id, request.message, limit=3)
    composed_context = None

    if faq_matches:
        top_score = float(faq_matches[0].get("score", 0) or 0)
        logger.info("Top FAQ score for query '%s': %.4f", request.message[:60], top_score)

        if top_score >= settings.FAQ_CONFIDENCE_THRESHOLD:
            # High confidence — return the best matching FAQ answer directly
            top_answer = (faq_matches[0].get("answer") or "").strip()
            if top_answer:
                assistant_msg = await db.save_message(conversation_id, "assistant", top_answer)
                return ChatResponse(
                    response=top_answer,
                    conversation_id=conversation_id,
                    user_message_id=str(user_msg["id"]),
                    assistant_message_id=str(assistant_msg["id"]),
                )

        # Lower confidence — pass FAQ matches as context to LLM for a nuanced answer
        faq_context = _build_faq_context(faq_matches)
        composed_context = f"--- FAQ Matches ---\n{faq_context}"

    if not settings.GROQ_API_KEY:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY is not configured.")

    try:
        ai_response = await groq_service.groq_service.chat(
            user_message=request.message,
            history=history_dicts,
            document_context=composed_context,
        )
    except RuntimeError as error:
        logger.warning("LLM failed: %s", error)
        raise HTTPException(status_code=503, detail=str(error))

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

    # Seed FAQ data for this user if missing, then search
    await _ensure_user_faq_seeded(user_id)
    faq_matches = await db.search_faq_entries(user_id, request.message, limit=3)
    composed_context = None
    if faq_matches:
        faq_context = _build_faq_context(faq_matches)
        composed_context = f"--- FAQ Matches ---\n{faq_context}"

    # Check for human handoff intent
    intent_handoff = await _intent_handoff_message(user_id, conversation_id, request.message)
    if intent_handoff:
        async def intent_only_stream():
            yield f"data: {json.dumps({'type': 'meta', 'conversation_id': conversation_id})}\n\n"
            await db.save_message(conversation_id, "assistant", intent_handoff)
            yield f"data: {json.dumps({'type': 'chunk', 'content': intent_handoff})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id})}\n\n"

        return StreamingResponse(intent_only_stream(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    async def generate():
        full_response = ""
        yield f"data: {json.dumps({'type': 'meta', 'conversation_id': conversation_id})}\n\n"

        if faq_matches:
            top_score = float(faq_matches[0].get("score", 0) or 0)
            logger.info("Top FAQ stream score for query '%s': %.4f", request.message[:60], top_score)
            if top_score >= settings.FAQ_CONFIDENCE_THRESHOLD:
                top_answer = (faq_matches[0].get("answer") or "").strip()
                if top_answer:
                    await db.save_message(conversation_id, "assistant", top_answer)
                    yield f"data: {json.dumps({'type': 'chunk', 'content': top_answer})}\n\n"
                    yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id})}\n\n"
                    return

        if not settings.GROQ_API_KEY:
            yield f"data: {json.dumps({'type': 'error', 'message': 'GROQ_API_KEY is not configured.'})}\n\n"
            return

        try:
            stream = groq_service.groq_service.stream_chat(
                user_message=request.message,
                history=history_dicts,
                document_context=composed_context,
            )
            async for chunk in stream:
                full_response += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        except RuntimeError as error:
            logger.warning("LLM streaming failed: %s", error)
            yield f"data: {json.dumps({'type': 'error', 'message': str(error)})}\n\n"
            return

        await db.save_message(conversation_id, "assistant", full_response)
        yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

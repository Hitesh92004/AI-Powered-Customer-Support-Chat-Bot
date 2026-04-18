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
from app.services import gemini_service, groq_service
from app.services.faq_service import load_faq_entries_from_dataset
from app.services import db_service as db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])


def _fallback_not_configured_message() -> str:
    return "No backup LLM provider is configured. Add both GROQ_API_KEY and GEMINI_API_KEY for failover."


def _primary_provider() -> str:
    provider = (settings.PRIMARY_LLM_PROVIDER or "groq").strip().lower()
    return provider if provider in {"groq", "gemini"} else "groq"


def _build_faq_context(faq_matches: list[dict]) -> str:
    parts = []
    for idx, item in enumerate(faq_matches, start=1):
        parts.append(f"FAQ #{idx}\nQ: {item['question']}\nA: {item['answer']}")
    return "\n\n".join(parts)


async def _ensure_user_faq_seeded(user_id: str) -> None:
    """
    Ensure user has at least one FAQ entry. If not, seed from server dataset.
    This helps deployments work immediately after boot without manual train call.
    """
    count = await db.get_faq_entries_count(user_id)
    if count > 0:
        return

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

    await _ensure_user_faq_seeded(user_id)
    faq_matches = await db.search_faq_entries(user_id, request.message, limit=3)
    composed_context = None
    if faq_matches:
        top_score = float(faq_matches[0].get("score", 0) or 0)
        if top_score < settings.FAQ_CONFIDENCE_THRESHOLD:
            ticket = await db.create_handoff_ticket(
                user_id=user_id,
                conversation_id=conversation_id,
                user_message=request.message,
                reason=f"Low FAQ confidence (score={top_score:.3f})",
            )
            handoff_message = (
                "I’m not fully confident about this answer from the FAQ knowledge base. "
                f"I have escalated this to a human support agent (ticket: {str(ticket['id'])[:8]})."
            )
            assistant_msg = await db.save_message(conversation_id, "assistant", handoff_message)
            return ChatResponse(
                response=handoff_message,
                conversation_id=conversation_id,
                user_message_id=str(user_msg["id"]),
                assistant_message_id=str(assistant_msg["id"]),
            )

        # Deterministic FAQ mode: reply directly from highest-ranked FAQ answer
        # so responses stay aligned with the trained dataset.
        top_answer = (faq_matches[0].get("answer") or "").strip()
        if top_answer:
            assistant_msg = await db.save_message(conversation_id, "assistant", top_answer)
            return ChatResponse(
                response=top_answer,
                conversation_id=conversation_id,
                user_message_id=str(user_msg["id"]),
                assistant_message_id=str(assistant_msg["id"]),
            )

        faq_context = _build_faq_context(faq_matches)
        composed_context = f"--- FAQ Matches ---\n{faq_context}"

    # Get AI response (primary provider + automatic fallback)
    provider = _primary_provider()
    try:
        if provider == "groq":
            if not settings.GROQ_API_KEY:
                raise RuntimeError("Groq is set as primary, but GROQ_API_KEY is missing.")
            ai_response = await groq_service.groq_service.chat(
                user_message=request.message,
                history=history_dicts,
                document_context=composed_context,
            )
        else:
            ai_response = await gemini_service.gemini_service.chat(
                user_message=request.message,
                history=history_dicts,
                document_context=composed_context,
            )
    except RuntimeError as primary_error:
        logger.warning("Primary LLM (%s) failed: %s", provider, primary_error)
        try:
            if provider == "groq":
                if not settings.GEMINI_API_KEY:
                    raise HTTPException(status_code=503, detail=_fallback_not_configured_message())
                ai_response = await gemini_service.gemini_service.chat(
                    user_message=request.message,
                    history=history_dicts,
                    document_context=composed_context,
                )
            else:
                if not settings.GROQ_API_KEY:
                    raise HTTPException(status_code=503, detail=_fallback_not_configured_message())
                ai_response = await groq_service.groq_service.chat(
                    user_message=request.message,
                    history=history_dicts,
                    document_context=composed_context,
                )
        except RuntimeError as fallback_error:
            raise HTTPException(status_code=503, detail=str(fallback_error))

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
    await _ensure_user_faq_seeded(user_id)
    faq_matches = await db.search_faq_entries(user_id, request.message, limit=3)
    composed_context = None
    if faq_matches:
        faq_context = _build_faq_context(faq_matches)
        composed_context = f"--- FAQ Matches ---\n{faq_context}"

    async def generate():
        full_response = ""
        yield f"data: {json.dumps({'type': 'meta', 'conversation_id': conversation_id})}\n\n"
        if faq_matches:
            top_score = float(faq_matches[0].get("score", 0) or 0)
            if top_score < settings.FAQ_CONFIDENCE_THRESHOLD:
                ticket = await db.create_handoff_ticket(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    user_message=request.message,
                    reason=f"Low FAQ confidence (score={top_score:.3f})",
                )
                handoff_message = (
                    "I’m not fully confident about this answer from the FAQ knowledge base. "
                    f"I have escalated this to a human support agent (ticket: {str(ticket['id'])[:8]})."
                )
                await db.save_message(conversation_id, "assistant", handoff_message)
                yield f"data: {json.dumps({'type': 'chunk', 'content': handoff_message})}\n\n"
                yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id})}\n\n"
                return
            top_answer = (faq_matches[0].get("answer") or "").strip()
            if top_answer:
                await db.save_message(conversation_id, "assistant", top_answer)
                yield f"data: {json.dumps({'type': 'chunk', 'content': top_answer})}\n\n"
                yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id})}\n\n"
                return
        provider = _primary_provider()
        try:
            if provider == "groq":
                if not settings.GROQ_API_KEY:
                    raise RuntimeError("Groq is set as primary, but GROQ_API_KEY is missing.")
                stream = groq_service.groq_service.stream_chat(
                    user_message=request.message,
                    history=history_dicts,
                    document_context=composed_context,
                )
            else:
                stream = gemini_service.gemini_service.stream_chat(
                    user_message=request.message,
                    history=history_dicts,
                    document_context=composed_context,
                )
            async for chunk in stream:
                full_response += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        except RuntimeError as primary_error:
            logger.warning("Primary streaming LLM (%s) failed: %s", provider, primary_error)
            try:
                if provider == "groq":
                    if not settings.GEMINI_API_KEY:
                        yield f"data: {json.dumps({'type': 'error', 'message': _fallback_not_configured_message()})}\n\n"
                        return
                    fallback_stream = gemini_service.gemini_service.stream_chat(
                        user_message=request.message,
                        history=history_dicts,
                        document_context=composed_context,
                    )
                else:
                    if not settings.GROQ_API_KEY:
                        yield f"data: {json.dumps({'type': 'error', 'message': _fallback_not_configured_message()})}\n\n"
                        return
                    fallback_stream = groq_service.groq_service.stream_chat(
                        user_message=request.message,
                        history=history_dicts,
                        document_context=composed_context,
                    )

                async for chunk in fallback_stream:
                    full_response += chunk
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            except RuntimeError as fallback_error:
                yield f"data: {json.dumps({'type': 'error', 'message': str(fallback_error)})}\n\n"
                return

        await db.save_message(conversation_id, "assistant", full_response)
        yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

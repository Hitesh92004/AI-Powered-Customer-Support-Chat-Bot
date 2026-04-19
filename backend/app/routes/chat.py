"""
Chat routes — POST /api/chat with streaming support.
Includes translation, sentiment, and order escalation pipelines.
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
from app.services.translation_service import detect_and_translate_to_english, translate_to_language
from app.services.sentiment_service import analyze_sentiment

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])


def _build_faq_context(faq_matches: list[dict]) -> str:
    parts = []
    for idx, item in enumerate(faq_matches, start=1):
        parts.append(f"FAQ #{idx}\nQ: {item['question']}\nA: {item['answer']}")
    return "\n\n".join(parts)


async def _ensure_user_faq_seeded(user_id: str) -> None:
    """Ensure user has FAQ entries seeded from server dataset."""
    try:
        entries = load_faq_entries_from_dataset(settings.FAQ_DATASET_PATH)
    except Exception as e:
        logger.warning("FAQ auto-seed skipped for user %s: %s", user_id, e)
        return

    source_name = settings.FAQ_DATASET_PATH.split("/")[-1]
    
    # Fast path: check count before checking each individually.
    count = await db.get_faq_entries_count(user_id)
    if count >= len(entries):
        return
        
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


async def _intent_handoff_message(
    user_id: str,
    conversation_id: str,
    user_message: str,
) -> str | None:
    """Checks for explicit human escalation using sklearn."""
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
    """Send a message and get a full AI response with full pipeline."""
    # 1. Setup conversation
    if request.conversation_id:
        conversation = await db.get_conversation_by_id(request.conversation_id, user_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found.")
        conversation_id = request.conversation_id
    else:
        title = request.message[:60] + ("..." if len(request.message) > 60 else "")
        conversation = await db.create_conversation(user_id, title)
        conversation_id = str(conversation["id"])

    # 2. Pipeline: Translate & Sentiment
    lang, eng_message = await detect_and_translate_to_english(request.message)
    sentiment = await analyze_sentiment(eng_message)

    # 3. Store user message
    user_msg = await db.save_message(
        conversation_id=conversation_id, 
        role="user", 
        content=request.message, 
        language=lang, 
        sentiment=sentiment
    )

    ticket_notice = ""
    # 4. Escalate if negative
    if sentiment == "negative":
        ticket = await db.create_ticket(user_id=user_id, issue=eng_message, priority="high")
        ticket_notice = f"\n\n[System Note: A support ticket #{str(ticket['id'])[:8]} has been automatically created to address your frustration.]"

    # 5. Intent and Context processing
    composed_context = ""
    
    # Check for exact handoff
    intent_handoff = await _intent_handoff_message(user_id, conversation_id, eng_message)
    if intent_handoff:
        ai_response = await translate_to_language(intent_handoff, lang)
        assistant_msg = await db.save_message(conversation_id, "assistant", ai_response, lang, "neutral")
        return ChatResponse(
            response=ai_response,
            conversation_id=conversation_id,
            user_message_id=str(user_msg["id"]),
            assistant_message_id=str(assistant_msg["id"]),
        )
        
    # Check for order context
    order_id = await intent_router_service.extract_order_id(eng_message)
    if order_id:
        order = await db.get_order_by_order_id(order_id)
        if order:
            composed_context += f"--- Order Database Info ---\nStatus: {order['status']}\nExpected Delivery: {order['expected_delivery']}\n\n"
        else:
            composed_context += f"--- Order Database Info ---\nNo order found matching ID: {order_id}\n\n"

    # Seed FAQ data for this user if missing, then search
    await _ensure_user_faq_seeded(user_id)
    faq_matches = await db.search_faq_entries(user_id, eng_message, limit=3)

    if faq_matches:
        top_score = float(faq_matches[0].get("score", 0) or 0)
        if top_score >= settings.FAQ_CONFIDENCE_THRESHOLD and not order_id:
            # High confidence FAQ match, return immediately (unless order context is needed)
            top_answer = (faq_matches[0].get("answer") or "").strip()
            if top_answer:
                english_response = top_answer + ticket_notice
                ai_response = await translate_to_language(english_response, lang)
                assistant_msg = await db.save_message(conversation_id, "assistant", ai_response, lang, "neutral")
                return ChatResponse(
                    response=ai_response,
                    conversation_id=conversation_id,
                    user_message_id=str(user_msg["id"]),
                    assistant_message_id=str(assistant_msg["id"]),
                )

        # Lower confidence — pass FAQ matches as context
        faq_context = _build_faq_context(faq_matches)
        composed_context += f"--- FAQ Matches ---\n{faq_context}"

    if not settings.GROQ_API_KEY:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY is not configured.")

    # Fetch history (last 10 limits applied at DB)
    history = await db.get_messages(conversation_id, limit=10)
    history_dicts = [{"role": m["role"], "content": m["content"]} for m in history if m["role"] in ["user", "assistant"]]

    try:
        raw_ai_response = await groq_service.groq_service.chat(
            user_message=eng_message,
            history=history_dicts,
            document_context=composed_context if composed_context else None,
        )
        raw_ai_response += ticket_notice
    except RuntimeError as error:
        logger.warning("LLM failed: %s", error)
        raise HTTPException(status_code=503, detail=str(error))

    # Translate back to UI language
    ai_response = await translate_to_language(raw_ai_response, lang)

    # Save assistant message
    assistant_msg = await db.save_message(conversation_id, "assistant", ai_response, lang, "neutral")

    return ChatResponse(
        response=ai_response,
        conversation_id=conversation_id,
        user_message_id=str(user_msg["id"]),
        assistant_message_id=str(assistant_msg["id"]),
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest, user_id: str = Depends(get_current_user)):
    """Note: Full pipeline support for streaming logic falls back to synchronous translation for simplicity."""
    return await chat(request, user_id)

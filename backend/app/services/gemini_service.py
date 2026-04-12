"""
Google Gemini API service — handles all LLM interactions.
"""
import asyncio
import logging
from typing import AsyncGenerator, List, Dict, Optional
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful, professional AI Customer Support Assistant. Your role is to:

1. Provide accurate, clear, and concise answers to customer questions
2. Be empathetic and understanding when customers have problems
3. Guide users through troubleshooting steps when needed
4. Escalate complex issues by recommending they contact a human agent
5. Maintain a friendly, professional tone at all times

Guidelines:
- Always acknowledge the customer's concern before providing a solution
- If you don't know something, be honest and suggest where they can find help
- Keep responses focused and avoid unnecessary lengthy explanations
- If a document context is provided, use it to give more accurate answers
- For technical issues, provide step-by-step instructions
- Format your responses clearly with markdown when helpful

You are representing a company that values customer satisfaction above all else."""


class GeminiService:
    """Wrapper for Google Gemini API calls with streaming support."""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL
        self.generation_config = {
            "max_output_tokens": settings.MAX_TOKENS,
            "temperature": settings.TEMPERATURE,
        }

    def _get_model(self, system_instruction: str):
        return genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction,
            generation_config=self.generation_config,
        )

    def _build_system_prompt(self, document_context: Optional[str] = None) -> str:
        system = SYSTEM_PROMPT
        if document_context:
            system += f"\n\n--- Relevant Document Context ---\n{document_context[:3000]}\n--- End of Context ---"
        return system

    def _build_gemini_history(self, history: List[Dict]) -> List[Dict]:
        """Convert flat history list to Gemini's role/parts format."""
        gemini_history = []
        for msg in history[-20:]:
            role = msg.get("role")
            if role == "user":
                gemini_history.append({"role": "user", "parts": [msg["content"]]})
            elif role == "assistant":
                gemini_history.append({"role": "model", "parts": [msg["content"]]})
        return gemini_history

    async def chat(
        self,
        user_message: str,
        history: Optional[List[Dict]] = None,
        document_context: Optional[str] = None,
    ) -> str:
        """Send a message and return the full response."""
        system = self._build_system_prompt(document_context)
        model = self._get_model(system)
        gemini_history = self._build_gemini_history(history or [])

        def _sync_call():
            chat_session = model.start_chat(history=gemini_history)
            response = chat_session.send_message(user_message)
            return response.text

        try:
            return await asyncio.to_thread(_sync_call)
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise RuntimeError(f"LLM service error: {str(e)}")

    async def stream_chat(
        self,
        user_message: str,
        history: Optional[List[Dict]] = None,
        document_context: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream a chat response chunk by chunk using an asyncio Queue."""
        system = self._build_system_prompt(document_context)
        model = self._get_model(system)
        gemini_history = self._build_gemini_history(history or [])
        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()

        def _stream_sync():
            try:
                chat_session = model.start_chat(history=gemini_history)
                response = chat_session.send_message(user_message, stream=True)
                for chunk in response:
                    text = getattr(chunk, "text", None)
                    if text:
                        asyncio.run_coroutine_threadsafe(queue.put(text), loop)
            except Exception as exc:
                asyncio.run_coroutine_threadsafe(queue.put(exc), loop)
            finally:
                asyncio.run_coroutine_threadsafe(queue.put(None), loop)

        loop.run_in_executor(None, _stream_sync)

        while True:
            item = await queue.get()
            if item is None:
                break
            if isinstance(item, Exception):
                logger.error(f"Gemini streaming error: {item}")
                raise RuntimeError(f"LLM streaming error: {str(item)}")
            yield item


# Singleton
gemini_service = GeminiService()

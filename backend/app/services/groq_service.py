"""
Groq API service — handles all LLM interactions.
"""
import logging
from typing import AsyncGenerator, List, Dict, Optional
from groq import AsyncGroq
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

You are representing a company that values customer satisfaction above all else."""


class GroqService:
    """Wrapper for Groq API calls with streaming support."""

    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE

    def _build_messages(
        self,
        user_message: str,
        history: Optional[List[Dict]] = None,
        document_context: Optional[str] = None,
    ) -> List[Dict]:
        """Build the messages array for the Groq API call."""
        messages = []

        # System prompt — augment with document context if provided
        system_content = SYSTEM_PROMPT
        if document_context:
            system_content += f"\n\n--- Relevant Document Context ---\n{document_context[:3000]}\n--- End of Context ---"

        messages.append({"role": "system", "content": system_content})

        # Add conversation history (limit to last 10 exchanges to stay within token limits)
        if history:
            for msg in history[-20:]:
                if msg.get("role") in ("user", "assistant"):
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"],
                    })

        # Add current user message
        messages.append({"role": "user", "content": user_message})
        return messages

    async def chat(
        self,
        user_message: str,
        history: Optional[List[Dict]] = None,
        document_context: Optional[str] = None,
    ) -> str:
        """Send a chat message and return the full response."""
        messages = self._build_messages(user_message, history, document_context)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise RuntimeError(f"LLM service error: {str(e)}")

    async def stream_chat(
        self,
        user_message: str,
        history: Optional[List[Dict]] = None,
        document_context: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream a chat response chunk by chunk."""
        messages = self._build_messages(user_message, history, document_context)

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
        except Exception as e:
            logger.error(f"Groq streaming error: {e}")
            raise RuntimeError(f"LLM streaming error: {str(e)}")


# Singleton instance
groq_service = GroqService()

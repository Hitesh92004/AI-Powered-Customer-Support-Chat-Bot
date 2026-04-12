"""
Supabase service — all database operations.
"""
import logging
from typing import Optional, List, Dict
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    """Create and return a Supabase client using the service role key."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


# Module-level client (reused across requests)
supabase: Client = get_supabase_client()


# ─── Conversation Operations ──────────────────────────────────────────────────

async def create_conversation(user_id: str, title: str = "New Conversation") -> Dict:
    """Create a new conversation for a user."""
    try:
        result = supabase.table("conversations").insert({
            "user_id": user_id,
            "title": title,
        }).execute()
        return result.data[0]
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise RuntimeError(f"Database error: {str(e)}")


async def get_conversations(user_id: str) -> List[Dict]:
    """Get all conversations for a user, ordered by most recent."""
    try:
        result = (
            supabase.table("conversations")
            .select("*, messages(count)")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .execute()
        )
        return result.data
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        raise RuntimeError(f"Database error: {str(e)}")


async def get_conversation_by_id(conversation_id: str, user_id: str) -> Optional[Dict]:
    """Get a single conversation by ID, verifying ownership."""
    try:
        result = (
            supabase.table("conversations")
            .select("*")
            .eq("id", conversation_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        return result.data
    except Exception as e:
        logger.warning(f"Conversation not found: {conversation_id}")
        return None


async def update_conversation_title(conversation_id: str, title: str) -> Dict:
    """Update the title of a conversation."""
    try:
        result = (
            supabase.table("conversations")
            .update({"title": title, "updated_at": "now()"})
            .eq("id", conversation_id)
            .execute()
        )
        return result.data[0]
    except Exception as e:
        logger.error(f"Error updating conversation title: {e}")
        raise RuntimeError(f"Database error: {str(e)}")


async def delete_conversation(conversation_id: str, user_id: str) -> bool:
    """Delete a conversation and all its messages."""
    try:
        supabase.table("conversations").delete().eq("id", conversation_id).eq("user_id", user_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise RuntimeError(f"Database error: {str(e)}")


# ─── Message Operations ───────────────────────────────────────────────────────

async def save_message(conversation_id: str, role: str, content: str) -> Dict:
    """Save a message to a conversation."""
    try:
        result = supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
        }).execute()

        # Update conversation's updated_at
        supabase.table("conversations").update({"updated_at": "now()"}).eq("id", conversation_id).execute()

        return result.data[0]
    except Exception as e:
        logger.error(f"Error saving message: {e}")
        raise RuntimeError(f"Database error: {str(e)}")


async def get_messages(conversation_id: str) -> List[Dict]:
    """Get all messages in a conversation, ordered chronologically."""
    try:
        result = (
            supabase.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .order("created_at", desc=False)
            .execute()
        )
        return result.data
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        raise RuntimeError(f"Database error: {str(e)}")


# ─── Document Operations ──────────────────────────────────────────────────────

async def save_document(
    user_id: str,
    filename: str,
    content: str,
    file_type: str,
    conversation_id: Optional[str] = None,
) -> Dict:
    """Save an uploaded document's metadata and extracted text."""
    try:
        result = supabase.table("documents").insert({
            "user_id": user_id,
            "conversation_id": conversation_id,
            "filename": filename,
            "content": content,
            "file_type": file_type,
        }).execute()
        return result.data[0]
    except Exception as e:
        logger.error(f"Error saving document: {e}")
        raise RuntimeError(f"Database error: {str(e)}")


async def get_documents_for_conversation(conversation_id: str) -> List[Dict]:
    """Get all documents attached to a conversation."""
    try:
        result = (
            supabase.table("documents")
            .select("*")
            .eq("conversation_id", conversation_id)
            .execute()
        )
        return result.data
    except Exception as e:
        logger.error(f"Error fetching documents: {e}")
        raise RuntimeError(f"Database error: {str(e)}")


# ─── Auth Helpers ─────────────────────────────────────────────────────────────

async def verify_user_token(token: str) -> Optional[str]:
    """Verify a Supabase JWT token and return the user_id."""
    try:
        user = supabase.auth.get_user(token)
        if user and user.user:
            return user.user.id
        return None
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        return None

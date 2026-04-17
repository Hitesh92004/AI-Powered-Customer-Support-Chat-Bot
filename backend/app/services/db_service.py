"""
Database service — asyncpg connection pool + all CRUD operations for Neon PostgreSQL.
"""
import asyncpg
import logging
from typing import Optional, List, Dict
from app.config import settings

logger = logging.getLogger(__name__)

# Module-level connection pool (initialized on startup)
_pool: Optional[asyncpg.Pool] = None


async def init_pool():
    """Initialize the asyncpg connection pool. Called on app startup."""
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=2,
        max_size=10,
        command_timeout=30,
    )
    logger.info("Database pool initialized.")


async def close_pool():
    """Close the connection pool. Called on app shutdown."""
    global _pool
    if _pool:
        await _pool.close()
        logger.info("Database pool closed.")


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool not initialized.")
    return _pool


# ─── Helper ──────────────────────────────────────────────────────────────────

def _row_to_dict(row) -> Dict:
    """Convert asyncpg Record to dict."""
    return dict(row) if row else None


def _rows_to_dicts(rows) -> List[Dict]:
    """Convert list of asyncpg Records to list of dicts."""
    return [dict(r) for r in rows]


# ─── User Operations ─────────────────────────────────────────────────────────

async def create_user(email: str, password_hash: str) -> Dict:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO users (email, password_hash) VALUES ($1, $2)
               RETURNING id, email, created_at""",
            email, password_hash
        )
        return _row_to_dict(row)


async def get_user_by_email(email: str) -> Optional[Dict]:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, email, password_hash, created_at FROM users WHERE email = $1",
            email
        )
        return _row_to_dict(row)


async def get_user_by_id(user_id: str) -> Optional[Dict]:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, email, created_at FROM users WHERE id = $1",
            user_id
        )
        return _row_to_dict(row)


# ─── Conversation Operations ──────────────────────────────────────────────────

async def create_conversation(user_id: str, title: str = "New Conversation") -> Dict:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO conversations (user_id, title) VALUES ($1, $2)
               RETURNING id, user_id, title, created_at, updated_at""",
            user_id, title
        )
        return _row_to_dict(row)


async def get_conversations(user_id: str) -> List[Dict]:
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT c.id, c.title, c.created_at, c.updated_at,
                      COUNT(m.id) AS message_count
               FROM conversations c
               LEFT JOIN messages m ON m.conversation_id = c.id
               WHERE c.user_id = $1
               GROUP BY c.id
               ORDER BY c.updated_at DESC""",
            user_id
        )
        return _rows_to_dicts(rows)


async def get_conversation_by_id(conversation_id: str, user_id: str) -> Optional[Dict]:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """SELECT id, user_id, title, created_at, updated_at
               FROM conversations
               WHERE id = $1 AND user_id = $2""",
            conversation_id, user_id
        )
        return _row_to_dict(row)


async def update_conversation_timestamp(conversation_id: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE conversations SET updated_at = NOW() WHERE id = $1",
            conversation_id
        )


async def delete_conversation(conversation_id: str, user_id: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM conversations WHERE id = $1 AND user_id = $2",
            conversation_id, user_id
        )


# ─── Message Operations ───────────────────────────────────────────────────────

async def save_message(conversation_id: str, role: str, content: str) -> Dict:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO messages (conversation_id, role, content)
               VALUES ($1, $2, $3)
               RETURNING id, conversation_id, role, content, created_at""",
            conversation_id, role, content
        )
        await update_conversation_timestamp(conversation_id)
        return _row_to_dict(row)


async def get_messages(conversation_id: str) -> List[Dict]:
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT id, conversation_id, role, content, created_at
               FROM messages
               WHERE conversation_id = $1
               ORDER BY created_at ASC""",
            conversation_id
        )
        return _rows_to_dicts(rows)


# ─── Document Operations ──────────────────────────────────────────────────────

async def save_document(
    user_id: str,
    filename: str,
    content: str,
    file_type: str,
    conversation_id: Optional[str] = None,
) -> Dict:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO documents (user_id, conversation_id, filename, content, file_type)
               VALUES ($1, $2, $3, $4, $5)
               RETURNING id, user_id, conversation_id, filename, file_type, created_at""",
            user_id, conversation_id, filename, content, file_type
        )
        return _row_to_dict(row)


async def get_documents_for_conversation(conversation_id: str) -> List[Dict]:
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT id, filename, file_type, created_at
               FROM documents WHERE conversation_id = $1""",
            conversation_id
        )
        return _rows_to_dicts(rows)


# ─── FAQ Operations ───────────────────────────────────────────────────────────

async def save_faq_entry(
    user_id: str,
    question: str,
    answer: str,
    source_document: Optional[str] = None,
) -> Dict:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO faq_entries (user_id, question, answer, source_document)
               VALUES ($1, $2, $3, $4)
               RETURNING id, user_id, question, answer, source_document, created_at""",
            user_id, question, answer, source_document
        )
        return _row_to_dict(row)


async def search_faq_entries(user_id: str, query: str, limit: int = 3) -> List[Dict]:
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, question, answer, source_document,
                   ts_rank(search_vector, plainto_tsquery('english', $2)) AS score
            FROM faq_entries
            WHERE user_id = $1
              AND search_vector @@ plainto_tsquery('english', $2)
            ORDER BY score DESC, updated_at DESC
            LIMIT $3
            """,
            user_id, query, limit
        )
        return _rows_to_dicts(rows)


# ─── Handoff Operations ───────────────────────────────────────────────────────

async def create_handoff_ticket(
    user_id: str,
    conversation_id: str,
    user_message: str,
    reason: str,
    status: str = "open",
) -> Dict:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO handoff_tickets (user_id, conversation_id, user_message, reason, status)
               VALUES ($1, $2, $3, $4, $5)
               RETURNING id, user_id, conversation_id, user_message, reason, status, created_at, resolved_at""",
            user_id, conversation_id, user_message, reason, status
        )
        return _row_to_dict(row)

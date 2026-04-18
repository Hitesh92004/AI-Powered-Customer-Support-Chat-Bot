-- ============================================================
-- AI Customer Support Chatbot — Neon PostgreSQL Schema
-- Run this in the Neon SQL Editor (console.neon.tech)
-- ============================================================

-- Enable UUID extension (available by default in Neon)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Users ---------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email         TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Conversations -------------------------------------------
CREATE TABLE IF NOT EXISTS conversations (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id     UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  title       TEXT DEFAULT 'New Conversation',
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Messages ------------------------------------------------
CREATE TABLE IF NOT EXISTS messages (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE NOT NULL,
  role            TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content         TEXT NOT NULL,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Documents -----------------------------------------------
CREATE TABLE IF NOT EXISTS documents (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id         UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  filename        TEXT NOT NULL,
  content         TEXT,
  file_type       TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 5. FAQ entries ------------------------------------------------
CREATE TABLE IF NOT EXISTS faq_entries (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id         UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  question        TEXT NOT NULL,
  answer          TEXT NOT NULL,
  source_document TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW(),
  search_vector   tsvector GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(question, '') || ' ' || coalesce(answer, ''))
  ) STORED
);

-- 6. Handoff tickets -------------------------------------------
CREATE TABLE IF NOT EXISTS handoff_tickets (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id         UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE NOT NULL,
  user_message    TEXT NOT NULL,
  reason          TEXT NOT NULL,
  status          TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved')),
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  resolved_at     TIMESTAMPTZ
);

-- ============================================================
-- Indexes for performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_conversations_user_id    ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at      ON messages(created_at ASC);
CREATE INDEX IF NOT EXISTS idx_documents_user_id        ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_conversation   ON documents(conversation_id);
CREATE INDEX IF NOT EXISTS idx_users_email              ON users(email);
CREATE INDEX IF NOT EXISTS idx_faq_entries_user_id      ON faq_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_faq_entries_search       ON faq_entries USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_handoff_user_id          ON handoff_tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_handoff_status           ON handoff_tickets(status);

-- ============================================================
-- Auto-update updated_at trigger
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER conversations_updated_at
  BEFORE UPDATE ON conversations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER faq_entries_updated_at
  BEFORE UPDATE ON faq_entries
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

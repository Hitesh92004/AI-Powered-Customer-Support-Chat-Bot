# AI Customer Support Chatbot

A production-ready AI Customer Support Chatbot built with **React + Vite** on the frontend, **Python FastAPI** on the backend, **Supabase** for database and auth, and **Groq API** (free tier) for LLM responses.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + Tailwind CSS v3 |
| Backend | Python 3.11+ + FastAPI |
| Database | Supabase (PostgreSQL) |
| LLM | Groq API — Mixtral 8x7B |
| Auth | Supabase Auth |
| Deployment | Vercel (frontend) + Render (backend) |

---

## Project Structure

```
chatbot-project/
├── frontend/                  # React + Vite
│   ├── src/
│   │   ├── components/        # Sidebar, ChatWindow, MessageBubble, MessageInput, DocumentUpload
│   │   ├── pages/             # LoginPage, ChatPage
│   │   ├── lib/               # supabase.js, api.js
│   │   └── contexts/          # AuthContext.jsx
│   ├── .env.example
│   └── vercel.json
│
├── backend/                   # Python FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routes/            # chat.py, conversations.py, documents.py
│   │   ├── services/          # groq_service.py, supabase_service.py, document_service.py
│   │   ├── models/            # schemas.py
│   │   └── middleware/        # auth.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
└── supabase/
    └── schema.sql             # Run this in Supabase SQL Editor
```

---

## 🚀 Setup Guide

### 1. Supabase Setup

1. Go to [supabase.com](https://supabase.com) and create a new project
2. In the **SQL Editor**, paste and run the contents of `supabase/schema.sql`
3. Go to **Project Settings → API** and note:
   - `Project URL`
   - `anon` public key
   - `service_role` secret key
4. Enable **Email Auth** under Authentication → Providers

### 2. Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Create an API key (free tier)

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and fill in env vars
copy .env.example .env
```

Edit `backend/.env`:
```env
GROQ_API_KEY=gsk_...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_ANON_KEY=eyJ...
FRONTEND_URL=http://localhost:5173
```

```bash
# Run backend
python run.py
# API running at http://localhost:8000
# Docs at http://localhost:8000/api/docs
```

### 4. Frontend Setup

```bash
cd frontend

# Copy and fill in env vars
copy .env.example .env
```

Edit `frontend/.env`:
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
VITE_API_URL=http://localhost:8000/api
```

```bash
# Install dependencies (already done if using this repo)
npm install

# Run frontend  
npm run dev
# App running at http://localhost:5173
```

---

## Deployment

### Backend → Render

1. Push code to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Settings:
   - **Root Directory**: `backend`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./Dockerfile`
5. Add environment variables (same as `.env` but with production values):
   - `GROQ_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
   - `SUPABASE_ANON_KEY`
   - `FRONTEND_URL` → your Vercel URL
6. Deploy — note your Render backend URL

### Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → **New Project**
2. Import your GitHub repo
3. Settings:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
4. Add environment variables:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
   - `VITE_API_URL` → your Render backend URL + `/api`
5. Deploy

---

## Features

- ✅ **Authentication** — Email/password via Supabase Auth
- ✅ **Multi-conversation** — Create, switch, and delete conversations
- ✅ **Streaming responses** — Real-time SSE streaming from Groq
- ✅ **Document upload** — PDF and TXT extraction for context
- ✅ **Conversation history** — Full history sent as LLM context
- ✅ **Dark theme** — Glassmorphism UI with Inter font
- ✅ **Responsive** — Works on mobile and desktop
- ✅ **Markdown rendering** — AI responses rendered as rich markdown

---

## API Reference

Base URL: `http://localhost:8000/api`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/chat` | Send message, get response |
| POST | `/chat/stream` | Send message, get SSE stream |
| GET | `/conversations` | List conversations |
| POST | `/conversations` | Create conversation |
| GET | `/conversations/{id}` | Get conversation + messages |
| DELETE | `/conversations/{id}` | Delete conversation |
| POST | `/documents/upload` | Upload PDF/TXT |

Interactive docs: `http://localhost:8000/api/docs`

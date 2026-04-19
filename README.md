<div align="center">
  <img src="https://ui-avatars.com/api/?name=AI&background=6366f1&color=fff&size=128&rounded=true" alt="AI Chatbot Logo" width="100"/>
  
  # AI Support Agent Platform 🚀
  
  <p><b>An enterprise-ready Agentic AI platform integrating Scikit-learn intent routing, automated sentiment-based escalation, serverless RAG, and multi-lingual translation middleware.</b></p>
  
  <p>
    <a href="https://ai-powered-customer-support-chat-bo.vercel.app/" target="_blank"><img src="https://img.shields.io/badge/Live_Demo-FF4B4B?style=for-the-badge&logoColor=white" alt="Live Demo" /></a>
    <br/>
    <i>Note: Live demo uses Frictionless Anonymous Sessions. Auth is provided in source but bypassed for ease of review.</i>
  </p>

  <p>
    <img alt="React" src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
    <img alt="Tailwind CSS" src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" />
    <img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
    <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
    <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" />
  </p>
</div>

---

## 🌟 Pitch & Architecture

This application simulates a cutting-edge customer service AI agent for e-commerce. It uses modern architectures over archaic single-prompt LLM setups:

1. **Translation & Sentiment Pipeline:** Every query passes through a dual-middleware layer. It detects the language (e.g., Hindi/Spanish) and translates it for internal processing, while secondary **LLM-based sentiment analysis** monitors for user frustration.
2. **Intent Extraction & Escalation:** Uses a custom `scikit-learn` Logistic Regression ML model to predict human intervention needs. If sentiment is negative, it triggers an **automated ticket escalation** in the database before the LLM even responds.
3. **Retrieval-Augmented Generation (RAG):** Utilizes **Neon PostgreSQL's full-text search** to query a proprietary FAQ dataset, seeding the Llama-3-70B model with localized knowledge context to prevent hallucinations.

```mermaid
graph TD
    A[User React UI] --> B{Middleware}
    B -- Translation --> C[English Context]
    B -- Sentiment --> D{Is Negative?}
    D -- Yes --> E[Auto-Ticket Neon DB]
    C --> F{Intent Router ML}
    F -- Escalation --> E
    F -- Support --> G[Neon FAQ Search]
    G -- RAG Context --> H((Groq LPU LLM))
    H -- Stream Response --> I[Translation Layer]
    I --> A
```

---

## ✨ Features
- **Automated Sentiment Escalation:** Real-time sentiment analysis monitors user tone, automatically creating high-priority support tickets in PostgreSQL for frustrated customers.
- **Cross-Lingual Intelligence:** Built-in translation pipe supporting English and Hindi, allowing the agent to process global queries while maintaining internal consistency.
- **Hybrid Intent Routing:** Combines 'classical' ML (Scikit-Learn) for high-precision routing with Generative AI (Groq/Llama-3) for conversational depth.
- **RAG FAQ Context:** Loads dynamic JSON datasets into an asyncpg Postgres pool for accurate, zero-hallucination semantic answering.
- **Real-Time Token Streaming:** Server-Sent Events (SSE) provide a ChatGPT-like responsive UI rather than blocking HTTP awaits.
- **Dynamic Glassmorphic UI:** A beautifully customized Tailwind interface with pulsing animations, scrollable modals, and markdown support.

---

## 🚀 Setup Guide

### 1. Database Setup (Neon PostgreSQL)

1. Go to [neon.tech](https://neon.tech) and create a new project.
2. In the **SQL Editor**, paste and run the contents of `neon/schema.sql`.
3. Note your connection string (`postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require`).

### 2. Groq LLM Inference Setup

1. Go to [console.groq.com](https://console.groq.com)
2. Create a free API key. This drives our Llama-3-70B model.

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies (FastAPI, Groq, Scikit-learn, etc.)
pip install -r requirements.txt

# Copy and fill in env vars
copy .env.example .env
```

Edit `backend/.env`:
```env
DATABASE_URL=postgresql://user:pass@ep-....aws.neon.tech/neondb?sslmode=require
GROQ_API_KEY=gsk_...
JWT_SECRET_KEY=generate_a_random_secure_hex
JWT_EXPIRE_MINUTES=10080
FRONTEND_URL=http://localhost:5173
# ML Route
ENABLE_INTENT_ROUTER=true
```

**Train the ML Scikit-Learn Model:**
```bash
python scripts/train_intent_model.py --dataset data/faq_dataset.json --output models/intent_router.joblib
```

**Boot the Server:**
```bash
python run.py
# API running at http://localhost:8000
```

### 4. Frontend Setup

```bash
cd frontend

# Copy and fill env vars
copy .env.example .env
```
*(Ensure `VITE_API_URL=http://localhost:8000/api` is listed)*

```bash
# Install NPM dependencies
npm install

# Run frontend  
npm run dev
# App running at http://localhost:5173
```

---

## ☁️ Deployment Architecture

### Backend → Render
This backend is Dockerized for massive stability across deployment clouds.
1. Sync repository to Render.
2. In the service setup config:
   - **Root Directory**: `backend`
   - **Environment**: `Docker`
3. Add environment variables verbatim from your local `.env`.
4. Deploy the service.

### Frontend → Vercel
1. Sync repository to Vercel workspace.
2. Select **Vite** Framework.
3. Configure **Root Directory** as `frontend`.
4. Map `VITE_API_URL` to the public HTTPS backend URL generated via Render *(Remember: No trailing slashes).*
5. Deploy.

---

> Built rigorously to scale and demonstrate robust state-of-the-art engineering. Open an issue or fork if you find ways to optimize!

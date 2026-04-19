<div align="center">
  <img src="https://ui-avatars.com/api/?name=AI&background=6366f1&color=fff&size=128&rounded=true" alt="AI Chatbot Logo" width="100"/>
  
  # AI Support Agent Platform 🚀
  
  <p><b>An enterprise-ready AI chatbot integrating advanced Machine Learning (Scikit-learn) intention routing, Serverless PostgreSQL vector search for RAG, and lighting-fast Groq LLM streaming.</b></p>
  
  <p>
    <a href="https://ai-powered-customer-support-chat-bo.vercel.app/" target="_blank"><img src="https://img.shields.io/badge/Live_Demo-FF4B4B?style=for-the-badge&logoColor=white" alt="Live Demo" /></a>
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

1. **Intent Extraction:** Uses a custom `scikit-learn` Logistic Regression ML model (TF-IDF vectorizer) to predict if a user is frustrated or needs human intervention, triggering an immediate database handoff ticket instead of wasting token context.
2. **Retrieval-Augmented Generation (RAG):** When interacting, it utilizes **Neon PostgreSQL's full-text/vector search** to query a proprietary FAQ dataset, mapping identical issues and seeding the LLM with localized rules context first.
3. **Groq LPU Acceleration:** The final augmented query is orchestrated through **Groq (Llama 3 70B)** to provide practically instant chunked SSE token streaming to the beautiful glassmorphic React frontend.

```mermaid
graph LR
    A[User UI React] -- SSE Stream --> B(FastAPI Backend)
    B -- TF-IDF NLP --> C{Intent Router ML}
    C -- Escalate --> D[Human Handoff Ticket DB]
    C -- Support --> E[Neon PG Search]
    E -- RAG Context --> F((Groq Llama 3 LLM))
    F -- Real-Time Response --> A 
```

---

## ✨ Features
- **Custom JWT Auth:** Full-blown authentication pipeline equipped with bcrypt hashing and Python-JOSE encryption.
- **RAG FAQ Context:** Loads dynamic JSON datasets natively into an asyncpg Postgres pool for accurate, zero-hallucination semantic answering.
- **Real-Time Token Streaming:** Server-Sent Events (SSE) provide a ChatGPT-like responsive UI rather than blocking HTTP awaits.
- **Dynamic Glassmorphic UI:** A beautifully customized Tailwind interface with pulsing animations, scrollable modals, and markdown chat bubbles.

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

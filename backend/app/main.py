"""
FastAPI application entry point with Neon DB lifespan management.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.services.db_service import init_pool, close_pool
from app.routes import chat, conversations, documents, auth, faq

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage DB pool lifecycle: open on startup, close on shutdown."""
    logger.info("Starting up — connecting to Neon database...")
    await init_pool()
    yield
    logger.info("Shutting down — closing database pool...")
    await close_pool()


app = FastAPI(
    title="AI Customer Support Chatbot API",
    description="REST API powered by Groq + Neon PostgreSQL.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(documents.router)
app.include_router(faq.router)


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "groq_configured": bool(settings.GROQ_API_KEY),
        "primary_llm_provider": settings.PRIMARY_LLM_PROVIDER,
        "db_connected": bool(settings.DATABASE_URL),
    }


@app.get("/", tags=["Root"])
async def root():
    return {"message": "AI Customer Support Chatbot API. Visit /api/docs for documentation."}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})

"""
Documents routes — file upload, PDF/TXT text extraction.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import Optional

from app.middleware.auth import get_current_user
from app.models.schemas import DocumentUploadResponse
from app.services import supabase_service as db
from app.services.document_service import process_document
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["Documents"])

ALLOWED_TYPES = {"application/pdf", "text/plain", "application/octet-stream"}
ALLOWED_EXTENSIONS = {".pdf", ".txt"}


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None),
    user_id: str = Depends(get_current_user),
):
    """
    Upload a PDF or TXT document.
    Extracts text and saves to Supabase.
    Optionally attach to a conversation.
    """
    # Validate file extension
    filename = file.filename or "unknown"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{ext}'. Only PDF and TXT files are allowed.",
        )

    # Read file content
    file_bytes = await file.read()

    # Check file size
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB.",
        )

    # Process document
    try:
        content, file_type = process_document(
            file_bytes=file_bytes,
            filename=filename,
            content_type=file.content_type or "",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    # Save to Supabase
    doc = await db.save_document(
        user_id=user_id,
        filename=filename,
        content=content,
        file_type=file_type,
        conversation_id=conversation_id,
    )

    return DocumentUploadResponse(
        id=doc["id"],
        filename=filename,
        file_type=file_type,
        content_preview=content[:300] + ("..." if len(content) > 300 else ""),
        char_count=len(content),
        conversation_id=conversation_id,
    )


@router.get("/conversation/{conversation_id}")
async def get_conversation_documents(
    conversation_id: str,
    user_id: str = Depends(get_current_user),
):
    """Get all documents attached to a conversation."""
    docs = await db.get_documents_for_conversation(conversation_id)
    return {"documents": docs, "total": len(docs)}

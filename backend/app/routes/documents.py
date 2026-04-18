"""
Documents routes — file upload using Neon db_service.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import Optional
from app.middleware.auth import get_current_user
from app.models.schemas import DocumentUploadResponse
from app.services import db_service as db
from app.services.document_service import process_document
from app.config import settings

router = APIRouter(prefix="/api/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None),
    user_id: str = Depends(get_current_user),
):
    if not settings.ENABLE_USER_FILE_UPLOADS:
        raise HTTPException(
            status_code=403,
            detail="User file uploads are disabled for this deployment.",
        )

    filename = file.filename or "unknown"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail=f"Only PDF and TXT files are allowed.")

    file_bytes = await file.read()
    if len(file_bytes) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_FILE_SIZE_MB}MB limit.")

    try:
        content, file_type = process_document(file_bytes, filename, file.content_type or "")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    doc = await db.save_document(
        user_id=user_id, filename=filename, content=content,
        file_type=file_type, conversation_id=conversation_id,
    )

    return DocumentUploadResponse(
        id=str(doc["id"]), filename=filename, file_type=file_type,
        content_preview=content[:300] + ("..." if len(content) > 300 else ""),
        char_count=len(content), conversation_id=conversation_id,
    )


@router.get("/conversation/{conversation_id}")
async def get_conversation_documents(conversation_id: str, user_id: str = Depends(get_current_user)):
    docs = await db.get_documents_for_conversation(conversation_id)
    return {"documents": docs, "total": len(docs)}

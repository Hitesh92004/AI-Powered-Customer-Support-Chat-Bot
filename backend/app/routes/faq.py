"""
FAQ routes — upload/train FAQ data and handoff ticket listing.
"""
from pathlib import Path
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status

from app.middleware.auth import get_current_user
from app.models.schemas import FAQTrainResponse
from app.config import settings
from app.services.document_service import process_document
from app.services.faq_service import parse_faq_entries, load_faq_entries_from_dataset
from app.services import db_service as db

router = APIRouter(prefix="/api/faq", tags=["FAQ"])


@router.post("/train", response_model=FAQTrainResponse, status_code=status.HTTP_201_CREATED)
async def train_faq_from_file(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
):
    if not settings.ENABLE_USER_FILE_UPLOADS:
        raise HTTPException(
            status_code=403,
            detail="User file upload training is disabled. Use /api/faq/train-dataset instead.",
        )

    filename = file.filename or "faq.txt"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in {".txt", ".pdf"}:
        raise HTTPException(status_code=415, detail="Only PDF and TXT files are supported for FAQ training.")

    file_bytes = await file.read()
    try:
        content, _file_type = process_document(file_bytes, filename, file.content_type or "")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    entries = parse_faq_entries(content)
    if not entries:
        raise HTTPException(
            status_code=422,
            detail="No FAQ entries found. Use format: 'Q: ...' followed by 'A: ...'.",
        )

    inserted = 0
    for entry in entries:
        await db.save_faq_entry(
            user_id=user_id,
            question=entry["question"],
            answer=entry["answer"],
            source_document=filename,
        )
        inserted += 1

    return FAQTrainResponse(
        source_filename=filename,
        inserted=inserted,
        skipped=max(0, len(entries) - inserted),
        message="FAQ document trained successfully.",
    )


@router.post("/train-dataset", response_model=FAQTrainResponse, status_code=status.HTTP_201_CREATED)
async def train_faq_from_dataset(user_id: str = Depends(get_current_user)):
    dataset_path = settings.FAQ_DATASET_PATH
    try:
        entries = load_faq_entries_from_dataset(dataset_path)
    except (ValueError, OSError) as e:
        raise HTTPException(status_code=422, detail=str(e))

    if not entries:
        raise HTTPException(status_code=422, detail="No valid FAQ entries found in dataset.")

    inserted = 0
    skipped = 0
    source_name = Path(dataset_path).name
    for entry in entries:
        if await db.faq_entry_exists(user_id=user_id, question=entry["question"]):
            skipped += 1
            continue
        await db.save_faq_entry(
            user_id=user_id,
            question=entry["question"],
            answer=entry["answer"],
            source_document=source_name,
        )
        inserted += 1

    return FAQTrainResponse(
        source_filename=source_name,
        inserted=inserted,
        skipped=skipped,
        message="FAQ dataset trained successfully.",
    )

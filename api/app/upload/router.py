import logging
import os
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import SessionLocal
from app.models.file import File as FileModel
from app.models.upload_session import UploadSession
from app.models.user import User
from app.rate_limit import limiter
from app.upload.schemas import (
    FileDetail,
    FileListItem,
    FileListResponse,
    FileUploadResponse,
    PresignedUrlRequest,
    PresignedUrlResponse,
    SessionStatusResponse,
    UploadCompleteResponse,
    UploadSessionResponse,
    UsageLimitResponse,
)
from app.upload.utils import R2StorageBackend, generate_presigned_upload_url, generate_storage_key, storage
from app.upload.validation import enqueue_content_validation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload")


from typing import Generator
from fastapi.responses import StreamingResponse

def _get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/session", response_model=UploadSessionResponse, status_code=201)
async def create_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
) -> UploadSessionResponse:
    session = UploadSession(user_id=current_user.id, status="pending")
    db.add(session)
    db.commit()
    db.refresh(session)

    logger.info("Created upload session %s for user %s", session.id, current_user.id)

    return UploadSessionResponse(
        session_id=session.id,
        status=session.status,
        file_count=session.file_count,
        max_files=settings.max_files_per_batch,
    )


@router.post("/{session_id}/files", response_model=FileUploadResponse, status_code=201, deprecated=True)
async def upload_file(
    session_id: uuid.UUID,
    file: UploadFile = File(...),
    classification: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
) -> FileUploadResponse:
    logger.warning("Deprecated endpoint POST /upload/{session_id}/files called — use POST /upload/presign-url instead")
    session = (
        db.query(UploadSession)
        .filter(UploadSession.id == session_id, UploadSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SESSION_NOT_FOUND", "message": "Session not found"},
        )

    if classification not in ("exam", "lecture"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CLASSIFICATION_REQUIRED",
                "message": "Each file must be classified as 'exam' or 'lecture'",
            },
        )

    content = await file.read()

    if len(content) > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "FILE_TOO_LARGE",
                "message": f"File exceeds {settings.max_file_size_mb} MB limit",
            },
        )

    if not content.startswith(b"%PDF"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_FILE_TYPE",
                "message": "Only PDF files are accepted",
            },
        )

    try:
        PdfReader(BytesIO(content))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_FILE_TYPE",
                "message": "File content is not a valid PDF",
            },
        )

    if session.file_count >= settings.max_files_per_batch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "BATCH_LIMIT_REACHED",
                "message": f"Maximum {settings.max_files_per_batch} files per batch",
            },
        )

    user = db.query(User).filter(User.id == current_user.id).with_for_update().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"},
        )

    plan_limit = settings.free_tier_file_limit
    if user.files_uploaded >= plan_limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "PLAN_LIMIT_REACHED",
                "message": "You have reached your upload limit. Upgrade your plan to upload more files.",
            },
        )

    file_id = uuid.uuid4()
    storage_key = generate_storage_key(current_user.id, file_id)

    await storage.save(storage_key, content)

    file_record = FileModel(
        id=file_id,
        user_id=current_user.id,
        upload_session_id=session.id,
        filename=file.filename or "untitled.pdf",
        storage_key=storage_key,
        file_size=len(content),
        classification=classification,
        mime_type="application/pdf",
        status="uploaded",
    )
    db.add(file_record)

    user.files_uploaded += 1
    session.file_count += 1

    if session.status == "pending":
        session.status = "uploading"

    db.commit()
    db.refresh(file_record)

    logger.info(
        "File %s uploaded by user %s, session %s",
        file_record.id,
        current_user.id,
        session.id,
    )

    return FileUploadResponse(
        file_id=file_record.id,
        filename=file_record.filename,
        file_size=file_record.file_size,
        classification=file_record.classification,
        status=file_record.status,
        created_at=file_record.created_at.isoformat(),
    )


@router.post("/presign-url", response_model=PresignedUrlResponse)
@limiter.limit("10/minute")
async def presign_upload_url(
    request: Request,
    body: PresignedUrlRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
) -> PresignedUrlResponse:
    if body.file_size > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "FILE_TOO_LARGE",
                "message": f"File exceeds {settings.max_file_size_mb} MB limit",
            },
        )

    user = db.query(User).filter(User.id == current_user.id).with_for_update().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"},
        )

    if user.files_uploaded >= settings.free_tier_file_limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "PLAN_LIMIT_REACHED",
                "message": f"You have reached your limit of {settings.free_tier_file_limit} stored files.",
            },
        )

    if user.analyses_used_this_month >= settings.free_tier_analysis_limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ANALYSIS_QUOTA_EXCEEDED",
                "message": f"Monthly analysis quota ({settings.free_tier_analysis_limit}) exhausted.",
            },
        )

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=30)
    session = (
        db.query(UploadSession)
        .filter(
            UploadSession.user_id == user.id,
            UploadSession.last_activity >= cutoff,
        )
        .order_by(UploadSession.last_activity.desc())
        .first()
    )
    if not session:
        session = UploadSession(user_id=user.id, status="pending", last_activity=now)
        db.add(session)
        db.flush()

    file_id = uuid.uuid4()
    storage_key = generate_storage_key(user.id, file_id)

    presigned_url = generate_presigned_upload_url(storage_key)

    file_record = FileModel(
        id=file_id,
        user_id=user.id,
        upload_session_id=session.id,
        filename=body.filename,
        storage_key=storage_key,
        file_size=body.file_size,
        classification=body.classification,
        mime_type="application/pdf",
        status="uploaded",
        validation_status="pending",
    )
    db.add(file_record)

    user.files_uploaded += 1
    session.last_activity = now
    if session.status == "pending":
        session.status = "uploading"

    db.commit()

    logger.info(
        "Presigned URL issued for file %s, user %s, session %s",
        file_id, user.id, session.id,
    )

    return PresignedUrlResponse(
        presigned_url=presigned_url,
        file_id=str(file_id),
        session_id=str(session.id),
        expires_in_seconds=900,
    )


@router.post("/{file_id}/complete", response_model=UploadCompleteResponse)
@limiter.limit("10/minute")
async def complete_upload(
    request: Request,
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
) -> UploadCompleteResponse:
    file_record = (
        db.query(FileModel)
        .filter(FileModel.id == file_id, FileModel.user_id == current_user.id)
        .first()
    )
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "FILE_NOT_FOUND", "message": "File not found"},
        )

    if file_record.validation_status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "ALREADY_COMPLETED",
                "message": "Upload already completed for this file",
            },
        )

    file_record.status = "uploaded"
    db.commit()

    enqueue_content_validation(str(file_id))

    logger.info("Upload completed for file %s, user %s", file_id, current_user.id)

    return UploadCompleteResponse(
        file_id=str(file_id),
        status=file_record.status,
        validation_status=file_record.validation_status,
    )


@router.get("/session/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
) -> SessionStatusResponse:
    session = (
        db.query(UploadSession)
        .filter(UploadSession.id == session_id, UploadSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SESSION_NOT_FOUND", "message": "Session not found"},
        )

    now = datetime.now(timezone.utc)
    inactive_cutoff = now - timedelta(minutes=30)
    if (
        session.status not in ("closed", "completed")
        and session.last_activity < inactive_cutoff
    ):
        session.status = "closed"
        db.commit()
        logger.info(
            "Session %s auto-closed after 30 min inactivity (last: %s)",
            session.id, session.last_activity,
        )

    files = (
        db.query(FileModel)
        .filter(FileModel.upload_session_id == session.id)
        .order_by(FileModel.created_at)
        .all()
    )

    file_details = [
        FileDetail(
            file_id=f.id,
            filename=f.filename,
            file_size=f.file_size,
            classification=f.classification,
            status=f.status,
            progress=100 if f.status == "uploaded" else 0,
        )
        for f in files
    ]

    return SessionStatusResponse(
        session_id=session.id,
        status=session.status,
        files=file_details,
    )


@router.get("/files", response_model=FileListResponse)
async def list_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
) -> FileListResponse:
    files = (
        db.query(FileModel)
        .filter(FileModel.user_id == current_user.id)
        .order_by(FileModel.created_at.desc())
        .all()
    )

    plan_limit = settings.free_tier_file_limit

    return FileListResponse(
        files=[
            FileListItem(
                file_id=f.id,
                filename=f.filename,
                file_size=f.file_size,
                classification=f.classification,
                status=f.status,
                validation_status=f.validation_status,
                session_id=f.upload_session_id,
                created_at=f.created_at.isoformat(),
            )
            for f in files
        ],
        total_count=len(files),
        plan_limit=plan_limit,
    )


@router.get("/limits", response_model=UsageLimitResponse)
async def get_limits(
    current_user: User = Depends(get_current_user),
) -> UsageLimitResponse:
    return UsageLimitResponse(
        files_uploaded=current_user.files_uploaded,
        plan_limit=settings.free_tier_file_limit,
        analyses_used=current_user.analyses_used_this_month,
        analyses_limit=settings.free_tier_analysis_limit,
    )


@router.get("/files/{file_id}/download")
async def download_file(
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
) -> StreamingResponse:
    file_record = (
        db.query(FileModel)
        .filter(FileModel.id == file_id, FileModel.user_id == current_user.id)
        .first()
    )
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "FILE_NOT_FOUND", "message": "File not found"},
        )

    from fastapi.responses import StreamingResponse

    content = await storage.read(file_record.storage_key)

    return StreamingResponse(
        iter([content]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{file_record.filename}"'
        },
    )


@router.put("/storage/{storage_key:path}")
async def local_storage_upload(
    storage_key: str,
    request: Request,
) -> dict[str, object]:
    if isinstance(storage, R2StorageBackend):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "NOT_AVAILABLE", "message": "Use R2 presigned URL directly"},
        )

    content = await request.body()
    full_path = os.path.join(settings.upload_storage_path, storage_key)
    dir_path = os.path.dirname(full_path)
    os.makedirs(dir_path, exist_ok=True)
    with open(full_path, "wb") as f:
        f.write(content)

    logger.info("Local storage upload: key=%s size=%d", storage_key, len(content))
    return {"success": True}

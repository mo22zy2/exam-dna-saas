from uuid import UUID

from pydantic import BaseModel, Field


class UploadSessionResponse(BaseModel):
    session_id: UUID
    status: str
    file_count: int
    max_files: int


class FileDetail(BaseModel):
    file_id: UUID
    filename: str
    file_size: int
    classification: str
    status: str
    progress: int
    client_upload_id: UUID | None = None


class SessionStatusResponse(BaseModel):
    session_id: UUID
    status: str
    files: list[FileDetail]


class FileUploadResponse(BaseModel):
    file_id: UUID
    filename: str
    file_size: int
    classification: str
    status: str
    created_at: str


class FileListItem(BaseModel):
    file_id: UUID
    filename: str
    file_size: int
    classification: str
    status: str | None = None
    validation_status: str | None = None
    session_id: UUID | None = None
    created_at: str


class FileListResponse(BaseModel):
    files: list[FileListItem]
    total_count: int
    plan_limit: int


class UsageLimitResponse(BaseModel):
    files_uploaded: int
    plan_limit: int
    analyses_used: int
    analyses_limit: int


class ErrorResponse(BaseModel):
    code: str
    message: str


class ErrorEnvelope(BaseModel):
    success: bool = False
    error: ErrorResponse


class SuccessEnvelope(BaseModel):
    success: bool = True
    data: dict[str, object]


class PresignedUrlRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    file_size: int = Field(..., gt=0)
    classification: str = Field(..., pattern=r"^(exam|lecture)$")


class PresignedUrlResponse(BaseModel):
    presigned_url: str
    file_id: str
    session_id: str
    expires_in_seconds: int


class UploadCompleteResponse(BaseModel):
    file_id: str
    status: str
    validation_status: str

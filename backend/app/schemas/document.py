import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    id: uuid.UUID
    filename: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    status: str
    page_count: int | None
    chunk_count: int | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
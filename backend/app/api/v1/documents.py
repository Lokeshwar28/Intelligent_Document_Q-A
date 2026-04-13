import uuid
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.document import DocumentListResponse, DocumentResponse, DocumentUploadResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])

# Hardcoded user_id for now — replaced with real auth in a later step
DEV_USER_ID = "dev-user-001"


@router.post("/", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    """Upload a PDF or text document for processing."""
    service = DocumentService(db)
    try:
        return await service.upload_document(file=file, user_id=DEV_USER_ID)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> DocumentListResponse:
    """List all documents for the current user."""
    service = DocumentService(db)
    return await service.list_documents(
        user_id=DEV_USER_ID, limit=limit, offset=offset
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """Get a single document by ID."""
    service = DocumentService(db)
    try:
        return await service.get_document(
            document_id=document_id, user_id=DEV_USER_ID
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
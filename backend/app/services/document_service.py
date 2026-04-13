import uuid
from fastapi import UploadFile
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from app.core.storage import get_storage
from app.models.document import Document, DocumentStatus
from app.schemas.document import DocumentUploadResponse, DocumentListResponse, DocumentResponse

log = structlog.get_logger()

ALLOWED_MIME_TYPES = {"application/pdf", "text/plain"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


class DocumentService:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.storage = get_storage()

    async def upload_document(
        self,
        file: UploadFile,
        user_id: str,
    ) -> DocumentUploadResponse:
        """Validate, upload to S3, create DB record, enqueue processing task."""
        await self._validate_file(file)

        contents = await file.read()
        file_size = len(contents)

        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size} bytes (max {MAX_FILE_SIZE})")

        # Upload to S3
        import io
        s3_key = self.storage.upload_file(
            file_obj=io.BytesIO(contents),
            filename=file.filename or "upload",
            content_type=file.content_type or "application/octet-stream",
            user_id=user_id,
        )

        # Create DB record
        document = Document(
            user_id=user_id,
            filename=self._safe_filename(file.filename or "upload"),
            original_filename=file.filename or "upload",
            s3_key=s3_key,
            file_size_bytes=file_size,
            mime_type=file.content_type or "application/octet-stream",
            status=DocumentStatus.PENDING,
        )
        self.db.add(document)
        await self.db.flush()  # get the ID without committing

        log.info(
            "document_created",
            document_id=str(document.id),
            user_id=user_id,
            filename=document.original_filename,
        )

        # Enqueue Celery processing task
        from app.tasks.process_document import process_document_task
        process_document_task.delay(str(document.id))

        return DocumentUploadResponse.model_validate(document)

    async def list_documents(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> DocumentListResponse:
        """List all documents for a user."""
        count_result = await self.db.execute(
            select(func.count(Document.id)).where(Document.user_id == user_id)
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        documents = list(result.scalars().all())

        return DocumentListResponse(
            documents=[DocumentResponse.model_validate(d) for d in documents],
            total=total,
        )

    async def get_document(
        self,
        document_id: uuid.UUID,
        user_id: str,
    ) -> DocumentResponse:
        """Fetch a single document, scoped to user."""
        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.user_id == user_id,
            )
        )
        document = result.scalar_one_or_none()
        if document is None:
            raise ValueError(f"Document {document_id} not found")
        return DocumentResponse.model_validate(document)

    async def _validate_file(self, file: UploadFile) -> None:
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise ValueError(
                f"Unsupported file type: {file.content_type}. "
                f"Allowed: {ALLOWED_MIME_TYPES}"
            )

    @staticmethod
    def _safe_filename(filename: str) -> str:
        """Strip path components from filename."""
        return filename.replace("/", "_").replace("\\", "_")
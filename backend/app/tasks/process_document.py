import asyncio
import uuid
from sqlalchemy import select
import structlog
from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.document import Document, DocumentStatus

log = structlog.get_logger()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_task(self, document_id: str) -> dict:
    """
    Celery task: orchestrates full document processing pipeline.
    Runs sync but calls async code via asyncio.run().
    """
    try:
        return asyncio.run(_process_document(document_id))
    except Exception as exc:
        log.error("process_document_failed", document_id=document_id, error=str(exc))
        raise self.retry(exc=exc)


async def _process_document(document_id: str) -> dict:
    """Async implementation of the processing pipeline."""
    from app.services.embedding_service import EmbeddingService
    from app.core.storage import get_storage

    doc_uuid = uuid.UUID(document_id)

    async with AsyncSessionLocal() as db:
        # Fetch document
        result = await db.execute(
            select(Document).where(Document.id == doc_uuid)
        )
        document = result.scalar_one_or_none()
        if document is None:
            raise ValueError(f"Document {document_id} not found")

        # Mark as processing
        document.status = DocumentStatus.PROCESSING
        await db.commit()

        try:
            # Download from S3
            storage = get_storage()
            file_bytes = storage.download_file(document.s3_key)

            # Parse, chunk, embed
            embedding_service = EmbeddingService()
            chunk_count, page_count = await embedding_service.process_document(
                document_id=document_id,
                file_bytes=file_bytes,
                mime_type=document.mime_type,
            )

            # Mark as ready
            document.status = DocumentStatus.READY
            document.chunk_count = chunk_count
            document.page_count = page_count
            await db.commit()

            log.info(
                "document_processed",
                document_id=document_id,
                chunks=chunk_count,
                pages=page_count,
            )
            return {"document_id": document_id, "chunks": chunk_count}

        except Exception as exc:
            document.status = DocumentStatus.FAILED
            document.error_message = str(exc)
            await db.commit()
            raise
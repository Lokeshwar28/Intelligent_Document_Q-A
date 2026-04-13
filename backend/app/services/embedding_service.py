import structlog
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import get_settings

log = structlog.get_logger()
settings = get_settings()


class EmbeddingService:
    """Handles document parsing, chunking, embedding, and vector store upsert."""

    def __init__(self) -> None:
        self.chroma_client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    async def process_document(
        self,
        document_id: str,
        file_bytes: bytes,
        mime_type: str,
    ) -> tuple[int, int]:
        """
        Full pipeline: parse → chunk → embed → upsert.
        Returns (chunk_count, page_count).
        """
        pages = self._parse(file_bytes, mime_type)
        page_count = len(pages)

        chunks, metadatas = self._chunk(pages, document_id)

        if not chunks:
            raise ValueError("No text extracted from document")

        chunk_count = await self._embed_and_upsert(chunks, metadatas, document_id)

        return chunk_count, page_count

    def _parse(self, file_bytes: bytes, mime_type: str) -> list[dict]:
        """Parse file bytes into list of {page_number, text} dicts."""
        if mime_type == "application/pdf":
            return self._parse_pdf(file_bytes)
        elif mime_type == "text/plain":
            return [{"page_number": 1, "text": file_bytes.decode("utf-8", errors="ignore")}]
        else:
            raise ValueError(f"Unsupported mime type: {mime_type}")

    def _parse_pdf(self, file_bytes: bytes) -> list[dict]:
        """Use PyMuPDF to extract text per page."""
        import fitz  # PyMuPDF

        pages = []
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text("text")
                if text.strip():
                    pages.append({"page_number": page_num, "text": text})
        return pages

    def _chunk(
        self,
        pages: list[dict],
        document_id: str,
    ) -> tuple[list[str], list[dict]]:
        """Split pages into chunks, preserving page number in metadata."""
        chunks: list[str] = []
        metadatas: list[dict] = []

        for page in pages:
            page_chunks = self.splitter.split_text(page["text"])
            for chunk in page_chunks:
                chunks.append(chunk)
                metadatas.append({
                    "document_id": document_id,
                    "page_number": page["page_number"],
                    "chunk_index": len(chunks) - 1,
                })

        return chunks, metadatas

    async def _embed_and_upsert(
        self,
        chunks: list[str],
        metadatas: list[dict],
        document_id: str,
    ) -> int:
        """Embed chunks using Voyage AI and upsert to Chroma."""
        import voyageai

        client = voyageai.Client(api_key=settings.voyage_api_key)

        batch_size = 128
        all_embeddings: list[list[float]] = []

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            result = client.embed(
                batch,
                model=settings.embedding_model,
                input_type="document",
            )
            all_embeddings.extend(result.embeddings)

        ids = [
            f"{document_id}_{meta['page_number']}_{meta['chunk_index']}"
            for meta in metadatas
        ]

        self.collection.upsert(
            ids=ids,
            embeddings=all_embeddings,
            documents=chunks,
            metadatas=metadatas,
        )

        log.info(
            "embeddings_upserted",
            document_id=document_id,
            chunk_count=len(chunks),
        )
        return len(chunks)

    async def query(
        self,
        query_text: str,
        document_id: str,
        top_k: int | None = None,
    ) -> list[dict]:
        """Embed query and retrieve top-k similar chunks from Chroma."""
        import voyageai

        k = top_k or settings.retrieval_top_k
        client = voyageai.Client(api_key=settings.voyage_api_key)

        result = client.embed(
            [query_text],
            model=settings.embedding_model,
            input_type="query",
        )
        query_embedding = result.embeddings[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where={"document_id": document_id},
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        for i, doc in enumerate(results["documents"][0]):
            chunks.append({
                "text": doc,
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })

        return chunks
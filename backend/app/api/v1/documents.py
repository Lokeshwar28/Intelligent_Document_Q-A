from fastapi import APIRouter

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/")
async def list_documents() -> dict:
    """Placeholder — full implementation in Step 2."""
    return {"documents": []}
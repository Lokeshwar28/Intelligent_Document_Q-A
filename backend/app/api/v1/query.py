from fastapi import APIRouter

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/")
async def query_document() -> dict:
    """Placeholder — full implementation in Step 3."""
    return {"answer": "not implemented yet"}
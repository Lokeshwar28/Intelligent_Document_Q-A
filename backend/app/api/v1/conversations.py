from fastapi import APIRouter

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/")
async def list_conversations() -> dict:
    """Placeholder — full implementation in Step 2."""
    return {"conversations": []}
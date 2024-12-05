from fastapi import APIRouter

router = APIRouter(prefix="/items", tags=["items"])


@router.get("")
def get_items_handler():
    return [
        {"id": 1, "name": "i-phone"},
        {"id": 2, "name": "samsung"},
    ]

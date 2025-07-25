from fastapi import APIRouter, Depends
from backend.core.security import bearer_auth

router = APIRouter()

@router.get("/", dependencies=[Depends(bearer_auth)])
async def get_notifications():
    # Logic to retrieve notifications data
    return []
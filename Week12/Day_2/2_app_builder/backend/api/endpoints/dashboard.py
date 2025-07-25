from fastapi import APIRouter, Depends
from backend.core.security import bearer_auth

router = APIRouter()

@router.get("/", dependencies=[Depends(bearer_auth)])
async def get_dashboard():
    # Logic to retrieve dashboard data
    return {"message": "Dashboard data"}
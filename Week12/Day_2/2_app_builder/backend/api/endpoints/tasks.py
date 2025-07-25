from fastapi import APIRouter, Depends, HTTPException
from backend.models.schemas import Task, CreateTaskRequest
from backend.core.security import bearer_auth

router = APIRouter()

@router.get("/", response_model=list[Task], dependencies=[Depends(bearer_auth)])
async def get_tasks():
    # Logic to retrieve task data
    return []

@router.post("/", response_model=Task, dependencies=[Depends(bearer_auth)])
async def create_task(task: CreateTaskRequest):
    # Logic to create task
    return {}
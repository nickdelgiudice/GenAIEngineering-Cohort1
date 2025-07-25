from fastapi import APIRouter, Depends, HTTPException
from backend.models.schemas import Task, CreateTaskRequest
from backend.core.security import bearer_auth

router = APIRouter()

@router.get("/", response_model=Task, dependencies=[Depends(bearer_auth)])
async def get_task(taskId: str):
    # Logic to retrieve single task
    return {}

@router.put("/", response_model=Task, dependencies=[Depends(bearer_auth)])
async def update_task(taskId: str, task: CreateTaskRequest):
    # Logic to update task
    return {}

@router.delete("/", dependencies=[Depends(bearer_auth)])
async def delete_task(taskId: str):
    # Logic to delete task
    return {}
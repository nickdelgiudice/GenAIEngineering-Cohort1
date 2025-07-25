from fastapi import APIRouter
from backend.api.endpoints import dashboard, notifications, reports, tasks, task_detail

api_router = APIRouter()

api_router.include_router(dashboard.router, tags=["Dashboard"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(task_detail.router, prefix="/tasks/{taskId}", tags=["Task Detail"])
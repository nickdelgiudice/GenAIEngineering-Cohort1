from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import api_router
from backend.core.security import verify_jwt

app = FastAPI(
    title="TaskMaster Pro API",
    description="A task management system that allows users to create, edit, and track tasks, set due dates, priorities, and assign tasks to team members.",
    version="1.0.0"
)

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router)

@app.middleware("http")
async def add_jwt_bearer_auth(request, call_next):
    return await verify_jwt(request, call_next)
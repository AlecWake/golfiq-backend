from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(
    title="GolfIQ Backend",
    description="Practice-to-course transfer analytics platform for golfers.",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")
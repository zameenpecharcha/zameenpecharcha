from fastapi import FastAPI

app = FastAPI(title="Comments Service")

# Import routes
from .api import comment_api

# Include routers
app.include_router(comment_api.router, prefix="/api/v1/comments", tags=["comments"]) 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.user_api import user_router
from app.api.comments_api import comments_router
from app.api.posts_api import posts_router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# API routes
app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
app.include_router(comments_router, prefix="/api/v1/comments", tags=["comments"])
app.include_router(posts_router, prefix="/api/v1/posts", tags=["posts"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.user_api import user_router
from app.api.comments_api import comments_router
from app.api.posts_api import posts_router
from app.api.property_api import property_router
from app.api.auth_api import router as auth_router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    expose_headers=["*"]  # Expose all headers
)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# API routes
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
app.include_router(comments_router, prefix="/api/v1/comments", tags=["comments"])
app.include_router(posts_router, prefix="/api/v1/posts", tags=["posts"])
app.include_router(property_router, prefix="/api/v1/properties", tags=["properties"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
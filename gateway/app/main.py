from fastapi import FastAPI
from app.api import user_api, comments_api
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Gateway Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_api.router, prefix="/api/v1/users", tags=["users"])
app.include_router(comments_api.router, prefix="/api/v1/comments", tags=["comments"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
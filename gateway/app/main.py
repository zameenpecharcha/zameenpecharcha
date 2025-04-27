from fastapi import FastAPI
from .api import user_api

app = FastAPI(title="Gateway Service")

# Include routers
app.include_router(user_api.router, prefix="/api/v1/users", tags=["users"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
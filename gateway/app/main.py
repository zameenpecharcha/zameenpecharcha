from fastapi import FastAPI
from app.api.user_api import user
import uvicorn
app = FastAPI()

app.include_router(user)

@app.get("/")
def is_live():
    return {"message": "Welcome to the FastAPI GraphQL Server!"}

if __name__ == "__main__":
    # Run the FastAPI application using Uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
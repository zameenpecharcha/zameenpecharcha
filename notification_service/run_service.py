import uvicorn
from app.grpc_server import serve

if __name__ == "__main__":
    # Start gRPC server in a separate thread
    import threading
    grpc_thread = threading.Thread(target=serve)
    grpc_thread.start()
    
    # Start FastAPI server
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 
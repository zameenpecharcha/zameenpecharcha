import uvicorn
import threading
from app import app
from app.service.grpc_server import serve

def run_grpc_server():
    serve()

if __name__ == "__main__":
    # Start gRPC server in a separate thread
    grpc_thread = threading.Thread(target=run_grpc_server)
    grpc_thread.start()

    # Start HTTP server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    ) 
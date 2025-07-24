import grpc
from concurrent import futures
import sys
import os

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.service.auth_service import AuthService
import app.proto_files.auth_pb2_grpc as auth_pb2_grpc

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    print("Auth service started on port 50052")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()

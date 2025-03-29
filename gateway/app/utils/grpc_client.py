import grpc
from app.proto_files.user import user_pb2, user_pb2_grpc

class UserServiceClient:
    def __init__(self):
        self.channel = grpc.insecure_channel("localhost:50051")
        self.stub = user_pb2_grpc.UserServiceStub(self.channel)

    def get_user(self, user_id):
        request = user_pb2.UserRequest(id=user_id)
        return self.stub.GetUser(request)

    def create_user(self, name, email, phone, password):
        request = user_pb2.CreateUserRequest(name=name, email=email, phone=phone, password=password)
        return self.stub.CreateUser(request)

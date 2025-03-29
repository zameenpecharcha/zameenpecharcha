import grpc
from concurrent import futures
from app.proto_files import user_pb2, user_pb2_grpc
from app.repository.user_repository import  get_user_by_id, create_user

class UserService(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        user = get_user_by_id(request.id)
        if not user:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            return user_pb2.UserResponse()

        return user_pb2.UserResponse(id=user.user_id, name=user.name, email=user.email, phone=user.phone)

    def CreateUser(self, request, context):
        user_id = create_user(request.name, request.email, request.phone, request.password)
        return user_pb2.UserResponse(id=user_id, name=request.name, email=request.email, phone=request.phone)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
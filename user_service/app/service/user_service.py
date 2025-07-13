import grpc
from concurrent import futures
from user_service.app.proto_files import user_pb2, user_pb2_grpc
from user_service.app.repository.user_repository import get_user_by_id, create_user

class UserService(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        try:
            if not isinstance(request.id, int):
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("User ID must be an integer")
                return user_pb2.UserResponse()

            user = get_user_by_id(request.id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.id} not found")
                return user_pb2.UserResponse()

            return user_pb2.UserResponse(
                id=user.user_id,
                name=user.name,
                email=user.email,
                phone=user.phone if user.phone else 0
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting user: {str(e)}")
            return user_pb2.UserResponse()

    def CreateUser(self, request, context):
        try:
            if not request.name or not request.email:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Name and email are required")
                return user_pb2.UserResponse()

            user_id = create_user(request.name, request.email, request.phone, request.password)
            return user_pb2.UserResponse(
                id=user_id,
                name=request.name,
                email=request.email,
                phone=request.phone
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating user: {str(e)}")
            return user_pb2.UserResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')
    print("Starting user service on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
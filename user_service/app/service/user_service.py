import grpc
import bcrypt
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
                phone=user.phone if user.phone else 0,
                role=user.role if user.role else "",
                location=user.location if user.location else ""
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting user: {str(e)}")
            return user_pb2.UserResponse()

    def CreateUser(self, request, context):
        try:
            # Validate required fields
            if not request.name or not request.email or not request.password:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Name, email, and password are required")
                return user_pb2.UserResponse()

            # Validate location format (latitude,longitude)
            if request.location:
                try:
                    lat, lon = request.location.split(',')
                    float(lat.strip())
                    float(lon.strip())
                except ValueError:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("Location must be in format 'latitude,longitude'")
                    return user_pb2.UserResponse()

            # Hash the password
            try:
                hashed_password = bcrypt.hashpw(request.password.encode(), bcrypt.gensalt()).decode('utf-8')
                print(f"Password hashed successfully for user: {request.email}")
            except Exception as e:
                print(f"Error hashing password: {str(e)}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Error processing password")
                return user_pb2.UserResponse()

            # Create user with hashed password
            user_id = create_user(
                name=request.name,
                email=request.email,
                phone=request.phone,
                password=hashed_password,  # Store hashed password
                role=request.role,
                location=request.location
            )
            
            print(f"User created successfully with ID: {user_id}")
            
            return user_pb2.UserResponse(
                id=user_id,
                name=request.name,
                email=request.email,
                phone=request.phone,
                role=request.role,
                location=request.location
            )
        except Exception as e:
            print(f"Error creating user: {str(e)}")
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
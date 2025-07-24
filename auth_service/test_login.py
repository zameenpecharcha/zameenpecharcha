import grpc
from app.proto_files.auth_pb2_grpc import AuthServiceStub
from app.proto_files.auth_pb2 import LoginRequest

def test_login():
    # Create a channel
    channel = grpc.insecure_channel('localhost:50052')
    
    # Create a stub (client)
    stub = AuthServiceStub(channel)
    
    # Create login request
    request = LoginRequest(
        email="Hello",
        password="Hello"
    )
    
    try:
        # Try to login
        print("\nAttempting login with:")
        print(f"Email: {request.email}")
        print(f"Password: {request.password}")
        
        response = stub.Login(request)
        
        if response.token:
            print("\nLogin successful!")
            print(f"Token: {response.token}")
            print(f"Refresh Token: {response.refresh_token}")
        else:
            print("\nLogin failed - no token received")
            
    except grpc.RpcError as e:
        print(f"\nRPC Error: {e.code()}")
        print(f"Details: {e.details()}")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    test_login() 
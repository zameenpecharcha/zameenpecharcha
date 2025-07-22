# User Service

A gRPC-based microservice for managing user accounts in the Zameen Pe Charcha platform.

## Features

- User creation and retrieval
- Professional role/occupation management
- Location tracking with Google Maps coordinates
- Secure password handling
- PostgreSQL database integration

## Prerequisites

- Python 3.8+
- PostgreSQL database
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd user_service
```

2. Install dependencies:
```bash
pip install -r requirement.txt
```

3. Set up environment variables:
Create a `.env` file in the user_service directory with the following variables:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

## Database Schema

The service uses the following database schema:

```sql
Table: users
- user_id (Integer, Primary Key, Auto-increment)
- name (String, 50 chars)
- email (String, 50 chars)
- phone (Integer)
- profile_photo (String, 50 chars)
- role (String, 50 chars)
- location (String, 50 chars)
- created_at (TIMESTAMP)
- bio (String, 50 chars)
- password (String, 50 chars)
```

## Running the Service

1. Generate Protocol Buffers:
```bash
python generate_proto.py
```

2. Start the service:
```bash
python run_service.py
```

The service will start on port 50051.

## API Documentation

### gRPC Service Definition

```protobuf
service UserService {
  rpc GetUser (UserRequest) returns (UserResponse);
  rpc CreateUser (CreateUserRequest) returns (UserResponse);
}
```

### API Methods

#### 1. Create User
- Method: `CreateUser`
- Request: `CreateUserRequest`
  ```protobuf
  message CreateUserRequest {
    string name = 1;
    string email = 2;
    int32 phone = 3;
    string password = 4;
    string role = 5;    // profession/role
    string location = 6; // format: "latitude,longitude"
  }
  ```
- Response: `UserResponse`
  ```protobuf
  message UserResponse {
    int32 id = 1;
    string name = 2;
    string email = 3;
    int32 phone = 4;
    string role = 5;
    string location = 6;
  }
  ```

#### 2. Get User
- Method: `GetUser`
- Request: `UserRequest`
  ```protobuf
  message UserRequest {
    int32 id = 1;
  }
  ```
- Response: `UserResponse` (same as above)

### Example Usage

Using a gRPC client (Python example):
```python
import grpc
from user_service.app.proto_files import user_pb2, user_pb2_grpc

# Create a channel
channel = grpc.insecure_channel('localhost:50051')

# Create a stub
stub = user_pb2_grpc.UserServiceStub(channel)

# Create a user
create_request = user_pb2.CreateUserRequest(
    name="John Doe",
    email="john@example.com",
    phone=1234567890,
    password="secure_password",
    role="Real Estate Agent",
    location="12.9716,77.5946"  # Bangalore coordinates
)
response = stub.CreateUser(create_request)

# Get a user
get_request = user_pb2.UserRequest(id=1)
user = stub.GetUser(get_request)
```

## Error Handling

The service returns appropriate gRPC status codes:
- `INVALID_ARGUMENT`: When required fields are missing or invalid
- `NOT_FOUND`: When requested user doesn't exist
- `INTERNAL`: For server-side errors

## Location Format

The location field expects coordinates in the format "latitude,longitude":
- Latitude: -90 to 90
- Longitude: -180 to 180
- Example: "12.9716,77.5946"

## Development

### Regenerating Protocol Buffers

After modifying the proto file (`user.proto`), regenerate the gRPC code:
```bash
python generate_proto.py
```

### Running Tests
```bash
# TODO: Add test commands
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]
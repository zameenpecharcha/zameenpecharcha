# Posts Service

A gRPC microservice for managing posts, comments, and media in the Zameen Pecharcha platform.

## Features

- Create, read, update, and delete posts
- Media management (images)
- Comments and replies
- Like/unlike functionality for posts and comments
- Search and filter posts
- Pagination support

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (for caching)
- Protocol Buffers compiler

### Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
GRPC_PORT=50053
```

4. Generate Protocol Buffer files:
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto_files/post.proto
```

5. Initialize database:
```bash
python app/utils/init_db.py
```

6. Run the service:
```bash
python run_service.py
```

## Database Schema

### Posts Table
```sql
CREATE TABLE posts (
    id BIGINT NOT NULL DEFAULT nextval('posts_id_seq') PRIMARY KEY,
    user_id BIGINT NOT NULL,
    content VARCHAR(2000),
    title VARCHAR(255),
    visibility VARCHAR(20),
    property_type VARCHAR(50),
    location VARCHAR(255),
    map_location VARCHAR(100),
    price NUMERIC(15,2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Post Media Table
```sql
CREATE TABLE post_media (
    id BIGINT NOT NULL DEFAULT nextval('post_media_id_seq') PRIMARY KEY,
    post_id BIGINT NOT NULL,
    media_type VARCHAR(50),
    media_url VARCHAR(500),
    media_order INTEGER,
    media_size BIGINT,
    caption VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);
```

### Comments Table
```sql
CREATE TABLE comments (
    id BIGINT NOT NULL DEFAULT nextval('comments_id_seq') PRIMARY KEY,
    post_id BIGINT NOT NULL,
    parent_comment_id BIGINT,
    comment VARCHAR(1000),
    user_id BIGINT NOT NULL,
    status VARCHAR(20),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    commented_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES comments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Post Likes Table
```sql
CREATE TABLE post_likes (
    id BIGINT NOT NULL DEFAULT nextval('post_likes_id_seq') PRIMARY KEY,
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    reaction_type VARCHAR(20),
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Comment Likes Table
```sql
CREATE TABLE comment_likes (
    id BIGINT NOT NULL DEFAULT nextval('comment_likes_id_seq') PRIMARY KEY,
    comment_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    reaction_type VARCHAR(20),
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## gRPC Endpoints

### Post Operations

#### CreatePost
Creates a new post with optional media attachments.

Request:
```protobuf
message PostCreateRequest {
    int64 user_id = 1;
    string title = 2;
    string content = 3;
    string visibility = 4;
    string property_type = 5;
    string location = 6;
    string map_location = 7;
    double price = 8;
    string status = 9;
    repeated PostMediaUpload media = 10;
}
```

Response:
```protobuf
message PostResponse {
    bool success = 1;
    string message = 2;
    Post post = 3;
}
```

#### GetPost
Retrieves a post by ID.

Request:
```protobuf
message PostRequest {
    int64 post_id = 1;
}
```

#### GetPostsByUser
Retrieves posts by user ID with pagination.

Request:
```protobuf
message GetPostsByUserRequest {
    int64 user_id = 1;
    int32 page = 2;
    int32 limit = 3;
}
```

#### SearchPosts
Searches posts with filters and pagination.

Request:
```protobuf
message SearchPostsRequest {
    string property_type = 1;
    string location = 2;
    double min_price = 3;
    double max_price = 4;
    string status = 5;
    int32 page = 6;
    int32 limit = 7;
}
```

### Media Operations

#### AddPostMedia
Adds media to an existing post.

Request:
```protobuf
message PostMediaRequest {
    int64 post_id = 1;
    repeated PostMediaUpload media = 2;
}
```

#### DeletePostMedia
Deletes media from a post.

Request:
```protobuf
message PostRequest {
    int64 post_id = 1;
}
```

### Comment Operations

#### CreateComment
Creates a new comment or reply.

Request:
```protobuf
message CommentCreateRequest {
    int64 post_id = 1;
    int64 parent_comment_id = 2;
    string comment = 3;
    int64 user_id = 4;
}
```

#### GetComments
Retrieves comments for a post with pagination.

Request:
```protobuf
message GetCommentsRequest {
    int64 post_id = 1;
    int32 page = 2;
    int32 limit = 3;
}
```

### Like Operations

#### LikePost/UnlikePost
Manages post likes.

Request:
```protobuf
message LikeRequest {
    int64 id = 1;
    int64 user_id = 2;
    string reaction_type = 3;
}
```

#### LikeComment/UnlikeComment
Manages comment likes.

Request:
```protobuf
message LikeRequest {
    int64 id = 1;
    int64 user_id = 2;
    string reaction_type = 3;
}
```

## Testing

### Using BloomRPC

1. Download BloomRPC from [GitHub Releases](https://github.com/bloomrpc/bloomrpc/releases)
2. Import the `proto_files/post.proto` file
3. Set the server address to `localhost:50053`
4. Select an endpoint and fill in the request parameters
5. Click "Play" to send the request

Example CreatePost request:
```json
{
  "user_id": 2,
  "title": "Beautiful House for Sale",
  "content": "3 bedroom house with garden",
  "visibility": "public",
  "property_type": "house",
  "location": "New York",
  "map_location": "40.7128,-74.0060",
  "price": 500000.0,
  "status": "active",
  "media": [
    {
      "media_type": "image",
      "media_data": {
        "type": "Buffer",
        "data": [72, 101, 108, 108, 111]
      },
      "media_order": 1,
      "caption": "Front view"
    }
  ]
}
```

## Error Handling

The service uses standard gRPC status codes:

- `NOT_FOUND`: Resource not found
- `INVALID_ARGUMENT`: Invalid input parameters
- `PERMISSION_DENIED`: User not authorized
- `INTERNAL`: Server error
- `UNAUTHENTICATED`: Authentication failed

Example error response:
```json
{
  "success": false,
  "message": "Post not found",
  "post": null
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License

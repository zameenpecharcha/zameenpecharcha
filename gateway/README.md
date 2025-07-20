# Gateway Service

This is the API Gateway service that provides a GraphQL interface to interact with the microservices.

## Prerequisites

- Python 3.x
- User Service running on port 50051
- Comments Service running on port 50053

## Installation

1. Install the required dependencies:
```bash
pip install -r requirement.txt
```

## Running the Service

1. Set the Python path and start the service:
```bash
# Windows PowerShell
$env:PYTHONPATH = "$PWD"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Linux/Mac
export PYTHONPATH=$PWD
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. The service will be available at:
- GraphQL Endpoint: http://localhost:8000/api/v1/users/graphql
- Comments GraphQL Endpoint: http://localhost:8000/api/v1/comments/graphql
- Health Check: http://localhost:8000/health

## User Service Endpoints

### Create User

Use this mutation to create a new user:

```graphql
mutation {
  createUser(
    name: "Hello221111",
    email: "Hello2211111",
    phone: 10,
    password: "Hello111",
    role: "Hello",
    location: "12333,34454"
  ) {
    userId
    name
    email
    phone
    role
    location
  }
}
```

Expected Response:
```json
{
  "data": {
    "createUser": {
      "userId": 12,
      "name": "Hello221111",
      "email": "Hello2211111",
      "phone": 10,
      "role": "Hello",
      "location": "12333,34454"
    }
  }
}
```

### Get User

Use this query to get user details:

```graphql
query {
  user(id: 12) {
    userId
    name
    email
    phone
    role
    location
  }
}
```

Expected Response:
```json
{
  "data": {
    "user": {
      "userId": 12,
      "name": "Hello221111",
      "email": "Hello2211111",
      "phone": 10,
      "role": "Hello",
      "location": "12333,34454"
    }
  }
}
```

## Comments Service Endpoints

### 1. Create Comment
Creates a new comment or reply to an existing comment.

**Mutation:**
```graphql
mutation {
  createComment(
    postId: "5401108a-e58f-4c26-9938-bde0984fb18e",
    userId: "bc90e095-837e-40f7-9226-a1fa587626eb",
    content: "Hello",
    parentCommentId: "b529ea5d-0410-48cb-813a-1a25d43b6a2c"  # Optional, for replies
  ) {
    commentId
    postId
    userId
    content
    parentCommentId
    createdAt
    updatedAt
    likeCount
  }
}
```

**Response:**
```json
{
  "data": {
    "createComment": {
      "commentId": "new-uuid",
      "postId": "5401108a-e58f-4c26-9938-bde0984fb18e",
      "userId": "bc90e095-837e-40f7-9226-a1fa587626eb",
      "content": "Hello",
      "parentCommentId": "b529ea5d-0410-48cb-813a-1a25d43b6a2c",
      "createdAt": 1708444800,
      "updatedAt": 1708444800,
      "likeCount": 0
    }
  }
}
```

### 2. Get Comment
Retrieves a specific comment by ID.

**Query:**
```graphql
query {
  comment(commentId: "b529ea5d-0410-48cb-813a-1a25d43b6a2c") {
    commentId
    postId
    userId
    content
    parentCommentId
    createdAt
    updatedAt
    likeCount
  }
}
```

### 3. Get Comments by Post
Retrieves all comments for a specific post.

**Query:**
```graphql
query {
  commentsByPost(postId: "5401108a-e58f-4c26-9938-bde0984fb18e") {
    commentId
    postId
    userId
    content
    parentCommentId
    createdAt
    updatedAt
    likeCount
  }
}
```

### 4. Get Comment Replies
Retrieves all replies to a specific comment.

**Query:**
```graphql
query {
  commentReplies(commentId: "b529ea5d-0410-48cb-813a-1a25d43b6a2c") {
    commentId
    postId
    userId
    content
    parentCommentId
    createdAt
    updatedAt
    likeCount
  }
}
```

### 5. Update Comment
Updates the content of an existing comment.

**Mutation:**
```graphql
mutation {
  updateComment(
    commentId: "b529ea5d-0410-48cb-813a-1a25d43b6a2c",
    content: "Updated content"
  ) {
    commentId
    content
    updatedAt
  }
}
```

### 6. Delete Comment
Deletes a specific comment.

**Mutation:**
```graphql
mutation {
  deleteComment(commentId: "b529ea5d-0410-48cb-813a-1a25d43b6a2c")
}
```

**Response:**
```json
{
  "data": {
    "deleteComment": true
  }
}
```

### 7. Like Comment
Adds a like to a comment from a specific user.

**Mutation:**
```graphql
mutation {
  likeComment(
    commentId: "b529ea5d-0410-48cb-813a-1a25d43b6a2c",
    userId: "bc90e095-837e-40f7-9226-a1fa587626eb"
  ) {
    commentId
    likeCount
  }
}
```

### 8. Unlike Comment
Removes a like from a comment.

**Mutation:**
```graphql
mutation {
  unlikeComment(
    commentId: "b529ea5d-0410-48cb-813a-1a25d43b6a2c",
    userId: "bc90e095-837e-40f7-9226-a1fa587626eb"
  ) {
    commentId
    likeCount
  }
}
```

## Testing Methods

1. **Using GraphQL Playground**:
   - For Users: http://localhost:8000/api/v1/users/graphql
   - For Comments: http://localhost:8000/api/v1/comments/graphql
   - Paste the query/mutation
   - Click the "Play" button

2. **Using cURL**:
```bash
# Create User
curl -X POST http://localhost:8000/api/v1/users/graphql \
-H "Content-Type: application/json" \
-d "{\"query\": \"mutation { createUser(name: \\\"Hello221111\\\", email: \\\"Hello2211111\\\", phone: 10, password: \\\"Hello111\\\", role: \\\"Hello\\\", location: \\\"12333,34454\\\") { userId name email phone role location } }\"}"

# Get User
curl -X POST http://localhost:8000/api/v1/users/graphql \
-H "Content-Type: application/json" \
-d "{\"query\": \"query { user(id: 12) { userId name email phone role location } }\"}"

# Create Comment
curl -X POST http://localhost:8000/api/v1/comments/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { createComment(postId: \"5401108a-e58f-4c26-9938-bde0984fb18e\", userId: \"bc90e095-837e-40f7-9226-a1fa587626eb\", content: \"Hello\") { commentId postId userId content createdAt updatedAt likeCount } }"
}'
```

3. **Using Postman or any API client**:
- URL: `http://localhost:8000/api/v1/users/graphql` or `http://localhost:8000/api/v1/comments/graphql`
- Method: POST
- Headers: `Content-Type: application/json`
- Body (raw JSON): Include the query/mutation in the format:
```json
{
  "query": "your_query_or_mutation_here"
}
```

## Service Dependencies

### User Service (gRPC) - Port 50051
- Handles user creation and retrieval
- Must be running for user operations

### Comments Service (gRPC) - Port 50053
- Handles comment operations
- Must be running for comment operations

## Field Descriptions

### User Fields
- `userId`: Unique identifier for the user
- `name`: User's full name
- `email`: User's email address
- `phone`: User's phone number
- `role`: User's role/profession
- `location`: User's location (latitude,longitude)

### Comment Fields
- `commentId`: Unique identifier for the comment (UUID)
- `postId`: ID of the post this comment belongs to (UUID)
- `userId`: ID of the user who created the comment (UUID)
- `content`: The text content of the comment
- `parentCommentId`: ID of the parent comment if this is a reply (UUID, optional)
- `createdAt`: Unix timestamp of when the comment was created
- `updatedAt`: Unix timestamp of when the comment was last updated
- `likeCount`: Number of likes on the comment

## Error Handling

The service returns GraphQL errors in the following format:
```json
{
  "errors": [
    {
      "message": "Error message here",
      "locations": [{"line": 2, "column": 3}],
      "path": ["fieldName"]
    }
  ]
}
```

Common error types:
### User Service Errors
- `USER_NOT_FOUND`: The requested user doesn't exist
- `USER_CREATION_FAILED`: Failed to create the user
- `INVALID_INPUT`: Invalid input data provided

### Comments Service Errors
- `COMMENT_NOT_FOUND`: The requested comment doesn't exist
- `COMMENT_CREATION_FAILED`: Failed to create the comment
- `COMMENT_UPDATE_FAILED`: Failed to update the comment
- `COMMENT_DELETION_FAILED`: Failed to delete the comment
- `COMMENT_LIKE_FAILED`: Failed to like the comment
- `COMMENT_UNLIKE_FAILED`: Failed to unlike the comment
# Gateway Service

This is the API Gateway service that provides a GraphQL interface to interact with the microservices.

## Prerequisites

- Python 3.x
- User Service running on port 50051
- Auth Service running on port 50052
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
- Auth GraphQL Endpoint: http://localhost:8000/api/v1/auth/graphql
- Users GraphQL Endpoint: http://localhost:8000/api/v1/users/graphql
- Comments GraphQL Endpoint: http://localhost:8000/api/v1/comments/graphql
- Health Check: http://localhost:8000/health

## Auth Service Endpoints

### Login

Use this mutation to login:

```graphql
mutation {
  login(email: "user@example.com", password: "yourpassword") {
    success
    token
    refreshToken
    message
  }
}
```

Expected Response:
```json
{
  "data": {
    "login": {
      "success": true,
      "token": "jwt_token_here",
      "refreshToken": "refresh_token_here",
      "message": "Login successful"
    }
  }
}
```

### Send OTP

Use this mutation to send OTP:

```graphql
mutation {
  sendOtp(email: "user@example.com") {
    success
    message
  }
}
```

Expected Response:
```json
{
  "data": {
    "sendOtp": {
      "success": true,
      "message": "OTP sent successfully"
    }
  }
}
```

### Verify OTP

Use this mutation to verify OTP:

```graphql
mutation {
  verifyOtp(email: "user@example.com", otpCode: "123456") {
    success
    token
    message
  }
}
```

Expected Response:
```json
{
  "data": {
    "verifyOtp": {
      "success": true,
      "token": "jwt_token_here",
      "message": "OTP verified successfully"
    }
  }
}
```

### Forgot Password

Use this mutation to initiate password reset:

```graphql
mutation {
  forgotPassword(email: "user@example.com") {
    success
    message
  }
}
```

Expected Response:
```json
{
  "data": {
    "forgotPassword": {
      "success": true,
      "message": "OTP sent successfully"
    }
  }
}
```

### Reset Password

Use this mutation to reset password:

```graphql
mutation {
  resetPassword(
    email: "user@example.com"
    otpCode: "123456"
    newPassword: "newpassword123"
  ) {
    success
    message
  }
}
```

Expected Response:
```json
{
  "data": {
    "resetPassword": {
      "success": true,
      "message": "Password reset successfully"
    }
  }
}
```

### Password Reset Flow

To reset a password, follow these steps:

1. Call `forgotPassword` mutation with the user's email:
```graphql
mutation {
  forgotPassword(email: "user@example.com") {
    success
    message
  }
}
```

2. User will receive an OTP (in development, check the auth service logs)

3. Use the OTP to reset the password with `resetPassword` mutation:
```graphql
mutation {
  resetPassword(
    email: "user@example.com"
    otpCode: "123456"  # Use the OTP received
    newPassword: "newpassword123"
  ) {
    success
    message
  }
}
```

Note: The OTP is valid for 5 minutes. Make sure to use the same email in both steps.

### Auth Service Error Types

Common error responses:
- `INVALID_CREDENTIALS`: Email or password is incorrect
- `USER_NOT_FOUND`: User does not exist
- `INVALID_OTP`: OTP is incorrect or expired
- `OTP_SEND_FAILED`: Failed to send OTP
- `PASSWORD_RESET_FAILED`: Failed to reset password

Example error response:
```json
{
  "errors": [
    {
      "message": "Invalid credentials",
      "locations": [{"line": 2, "column": 3}],
      "path": ["login"]
    }
  ],
  "data": {
    "login": null
  }
}
```

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

## Posts Service Endpoints

### 1. Create Post
Creates a new post.

**Mutation:**
```graphql
mutation {
  createPost(
    userId: "5807b553-ff97-48ba-88a9-6f3f69395667",
    title: "My First Post",
    content: "This is the content of my first post"
  ) {
    postId
    userId
    title
    content
    createdAt
    updatedAt
    likeCount
    commentCount
  }
}
```

**Response:**
```json
{
  "data": {
    "createPost": {
      "postId": "1",
      "userId": "5807b553-ff97-48ba-88a9-6f3f69395667",
      "title": "My First Post",
      "content": "This is the content of my first post",
      "createdAt": 1753009257,
      "updatedAt": 1753009257,
      "likeCount": 0,
      "commentCount": 0
    }
  }
}
```

### 2. Get Post
Retrieves a specific post by ID.

**Query:**
```graphql
query {
  post(postId: "1") {
    postId
    userId
    title
    content
    createdAt
    updatedAt
    likeCount
    commentCount
  }
}
```

**Response:**
```json
{
  "data": {
    "post": {
      "postId": "1",
      "userId": "5807b553-ff97-48ba-88a9-6f3f69395667",
      "title": "My First Post",
      "content": "This is the content of my first post",
      "createdAt": 1753009257,
      "updatedAt": 1753009257,
      "likeCount": 0,
      "commentCount": 0
    }
  }
}
```

### 3. Get Posts by User
Retrieves all posts by a specific user.

**Query:**
```graphql
query {
  postsByUser(userId: "5807b553-ff97-48ba-88a9-6f3f69395667") {
    postId
    userId
    title
    content
    createdAt
    updatedAt
    likeCount
    commentCount
  }
}
```

**Response:**
```json
{
  "data": {
    "postsByUser": [
      {
        "postId": "1",
        "userId": "5807b553-ff97-48ba-88a9-6f3f69395667",
        "title": "My First Post",
        "content": "This is the content of my first post",
        "createdAt": 1753009257,
        "updatedAt": 1753009257,
        "likeCount": 0,
        "commentCount": 0
      }
      // ... more posts
    ]
  }
}
```

### 4. Update Post
Updates an existing post.

**Mutation:**
```graphql
mutation {
  updatePost(
    postId: "1",
    title: "Updated Title",
    content: "Updated content for my post"
  ) {
    postId
    title
    content
    updatedAt
  }
}
```

**Response:**
```json
{
  "data": {
    "updatePost": {
      "postId": "1",
      "title": "Updated Title",
      "content": "Updated content for my post",
      "updatedAt": 1753009300
    }
  }
}
```

### 5. Delete Post
Deletes a specific post.

**Mutation:**
```graphql
mutation {
  deletePost(postId: "1")
}
```

**Response:**
```json
{
  "data": {
    "deletePost": true
  }
}
```

### 6. Like Post
Adds a like to a post.

**Mutation:**
```graphql
mutation {
  likePost(
    postId: "1",
    userId: "5807b553-ff97-48ba-88a9-6f3f69395667"
  ) {
    postId
    likeCount
  }
}
```

**Response:**
```json
{
  "data": {
    "likePost": {
      "postId": "1",
      "likeCount": 1
    }
  }
}
```

### 7. Unlike Post
Removes a like from a post.

**Mutation:**
```graphql
mutation {
  unlikePost(
    postId: "1",
    userId: "5807b553-ff97-48ba-88a9-6f3f69395667"
  ) {
    postId
    likeCount
  }
}
```

**Response:**
```json
{
  "data": {
    "unlikePost": {
      "postId": "1",
      "likeCount": 0
    }
  }
}
```

### Posts Service Error Responses

Common error responses for the posts service:

```json
{
  "errors": [
    {
      "message": "POST_NOT_FOUND: Post does not exist",
      "locations": [{"line": 2, "column": 3}],
      "path": ["post"]
    }
  ],
  "data": null
}
```

Error types:
- `POST_NOT_FOUND`: The requested post doesn't exist
- `POST_CREATION_FAILED`: Failed to create the post
- `POST_UPDATE_FAILED`: Failed to update the post
- `POST_DELETION_FAILED`: Failed to delete the post
- `POST_LIKE_FAILED`: Failed to like the post
- `POST_UNLIKE_FAILED`: Failed to unlike the post

### Testing Posts Service

You can test the posts service endpoints using:

1. GraphQL Playground at `http://localhost:8000/api/v1/posts/graphql`
2. cURL:
```bash
# Create Post
curl -X POST http://localhost:8000/api/v1/posts/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { createPost(userId: \"5807b553-ff97-48ba-88a9-6f3f69395667\", title: \"My First Post\", content: \"This is the content\") { postId title content } }"
}'

# Get Post
curl -X POST http://localhost:8000/api/v1/posts/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "query { post(postId: \"1\") { postId title content } }"
}'
```

3. Postman or any API client:
- URL: `http://localhost:8000/api/v1/posts/graphql`
- Method: POST
- Headers: `Content-Type: application/json`
- Body (raw JSON): Include the query/mutation in the format:
```json
{
  "query": "your_query_or_mutation_here"
}
```

## Property Service Endpoints

### 1. Create Property
Creates a new property listing.

**Mutation:**
```graphql
mutation {
  createProperty(
    userId: "5807b553-ff97-48ba-88a9-6f3f69395667",
    title: "Modern Villa with Pool",
    description: "Beautiful modern villa with swimming pool",
    price: 750000.0,
    location: "Miami Beach",
    propertyType: VILLA,
    status: ACTIVE,
    bedrooms: 4,
    bathrooms: 3,
    area: 3000.0,
    yearBuilt: 2022,
    images: ["image1.jpg", "image2.jpg"],
    amenities: ["Pool", "Garden", "Garage"],
    latitude: 25.7617,
    longitude: -80.1918,
    address: "123 Palm Avenue",
    city: "Miami",
    state: "Florida",
    country: "USA",
    zipCode: "33139"
  ) {
    propertyId
    title
    price
    location
    propertyType
    status
    bedrooms
    bathrooms
    area
  }
}
```

**Response:**
```json
{
  "data": {
    "createProperty": {
      "propertyId": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Modern Villa with Pool",
      "price": 750000.0,
      "location": "Miami Beach",
      "propertyType": "VILLA",
      "status": "ACTIVE",
      "bedrooms": 4,
      "bathrooms": 3,
      "area": 3000.0
    }
  }
}
```

### 2. Get Property
Retrieves a specific property by ID.

**Query:**
```graphql
query {
  property(propertyId: "123e4567-e89b-12d3-a456-426614174000") {
    propertyId
    userId
    title
    description
    price
    location
    propertyType
    status
    bedrooms
    bathrooms
    area
    yearBuilt
    images
    amenities
    createdAt
    updatedAt
    viewCount
    latitude
    longitude
    address
    city
    state
    country
    zipCode
  }
}
```

### 3. Search Properties
Search properties with various filters.

**Query:**
```graphql
query {
  searchProperties(
    query: "beach view",
    propertyType: VILLA,
    minPrice: 500000,
    maxPrice: 1000000,
    location: "Miami",
    minBedrooms: 3,
    minBathrooms: 2,
    minArea: 2000,
    maxArea: 5000
  ) {
    propertyId
    title
    price
    location
    propertyType
    bedrooms
    bathrooms
    area
  }
}
```

### 4. Update Property
Updates an existing property.

**Mutation:**
```graphql
mutation {
  updateProperty(
    propertyId: "123e4567-e89b-12d3-a456-426614174000",
    title: "Updated Villa Title",
    description: "Updated description",
    price: 800000.0,
    status: ACTIVE
  ) {
    propertyId
    title
    description
    price
    status
    updatedAt
  }
}
```

### 5. Delete Property
Deletes a specific property.

**Mutation:**
```graphql
mutation {
  deleteProperty(propertyId: "123e4567-e89b-12d3-a456-426614174000")
}
```

### 6. Increment View Count
Increments the view count of a property.

**Mutation:**
```graphql
mutation {
  incrementViewCount(propertyId: "123e4567-e89b-12d3-a456-426614174000") {
    propertyId
    viewCount
  }
}
```

### Property Service Enums

1. **PropertyType**:
   - `APARTMENT`
   - `VILLA`
   - `HOUSE`
   - `LAND`

2. **PropertyStatus**:
   - `ACTIVE`
   - `INACTIVE`
   - `SOLD`
   - `RENTED`

### Property Service Error Types

- `PROPERTY_NOT_FOUND`: The requested property doesn't exist
- `PROPERTY_CREATION_FAILED`: Failed to create the property
- `PROPERTY_UPDATE_FAILED`: Failed to update the property
- `PROPERTY_DELETION_FAILED`: Failed to delete the property
- `PROPERTY_SEARCH_FAILED`: Failed to search properties
- `VIEW_COUNT_UPDATE_FAILED`: Failed to update view count

### Testing Property Service

You can test the property service endpoints using:

1. GraphQL Playground at `http://localhost:8000/api/v1/properties/graphql`
2. cURL:
```bash
# Create Property
curl -X POST http://localhost:8000/api/v1/properties/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { createProperty(userId: \"5807b553-ff97-48ba-88a9-6f3f69395667\", title: \"Modern Villa with Pool\", description: \"Beautiful modern villa with swimming pool\", price: 750000.0, location: \"Miami Beach\", propertyType: VILLA, status: ACTIVE, bedrooms: 4, bathrooms: 3, area: 3000.0, yearBuilt: 2022, images: [\"image1.jpg\"], amenities: [\"Pool\"], latitude: 25.7617, longitude: -80.1918, address: \"123 Palm Avenue\", city: \"Miami\", state: \"Florida\", country: \"USA\", zipCode: \"33139\") { propertyId title price location } }"
}'

# Get Property
curl -X POST http://localhost:8000/api/v1/properties/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "query { property(propertyId: \"123e4567-e89b-12d3-a456-426614174000\") { propertyId title price location } }"
}'
```

3. Postman or any API client:
- URL: `http://localhost:8000/api/v1/properties/graphql`
- Method: POST
- Headers: `Content-Type: application/json`
- Body (raw JSON): Include the query/mutation in the format:
```json
{
  "query": "your_query_or_mutation_here"
}
```

### Property Service Dependencies

The property service must be running on port 50053 for these endpoints to work. Make sure to:
1. Initialize the database tables
2. Start the property service
3. Have proper environment variables set for database connection
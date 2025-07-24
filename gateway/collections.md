# API Collections

This document contains all the API endpoints organized by service. Each request includes a cURL command that can be imported into Postman.

## Auth Service Collection

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { login(email: \"Hello\", password: \"Hello\") { success token refreshToken message } }"
}'
```

### Send OTP
```bash
curl -X POST http://localhost:8000/api/v1/auth/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { sendOtp(email: \"Hello\") { success message } }"
}'
```

### Verify OTP
```bash
curl -X POST http://localhost:8000/api/v1/auth/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { verifyOtp(email: \"Hello\", otpCode: \"123456\") { success token message } }"
}'
```

### Forgot Password
```bash
curl -X POST http://localhost:8000/api/v1/auth/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { forgotPassword(emailOrPhone: \"Hello\") { success message } }"
}'
```

### Reset Password
```bash
curl -X POST http://localhost:8000/api/v1/auth/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { resetPassword(emailOrPhone: \"Hello\", otpCode: \"123456\", newPassword: \"newpassword123\") { success message } }"
}'
```

## User Service Collection

### Create User
```bash
curl -X POST http://localhost:8000/api/v1/users/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { createUser(name: \"Hello221111\", email: \"Hello2211111\", phone: 10, password: \"Hello111\", role: \"Hello\", location: \"12333,34454\") { userId name email phone role location } }"
}'
```

### Get User
```bash
curl -X POST http://localhost:8000/api/v1/users/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "query { user(id: 12) { userId name email phone role location } }"
}'
```

## Comments Service Collection

### Create Comment
```bash
curl -X POST http://localhost:8000/api/v1/comments/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { createComment(postId: \"5401108a-e58f-4c26-9938-bde0984fb18e\", userId: \"bc90e095-837e-40f7-9226-a1fa587626eb\", content: \"Hello\") { commentId postId userId content createdAt updatedAt likeCount } }"
}'
```

### Get Comment
```bash
curl -X POST http://localhost:8000/api/v1/comments/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "query { comment(commentId: \"b529ea5d-0410-48cb-813a-1a25d43b6a2c\") { commentId postId userId content parentCommentId createdAt updatedAt likeCount } }"
}'
```

### Get Comments by Post
```bash
curl -X POST http://localhost:8000/api/v1/comments/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "query { commentsByPost(postId: \"5401108a-e58f-4c26-9938-bde0984fb18e\") { commentId postId userId content parentCommentId createdAt updatedAt likeCount } }"
}'
```

### Get Comment Replies
```bash
curl -X POST http://localhost:8000/api/v1/comments/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "query { commentReplies(commentId: \"b529ea5d-0410-48cb-813a-1a25d43b6a2c\") { commentId postId userId content parentCommentId createdAt updatedAt likeCount } }"
}'
```

### Update Comment
```bash
curl -X POST http://localhost:8000/api/v1/comments/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { updateComment(commentId: \"b529ea5d-0410-48cb-813a-1a25d43b6a2c\", content: \"Updated content\") { commentId content updatedAt } }"
}'
```

### Delete Comment
```bash
curl -X POST http://localhost:8000/api/v1/comments/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { deleteComment(commentId: \"b529ea5d-0410-48cb-813a-1a25d43b6a2c\") }"
}'
```

### Like Comment
```bash
curl -X POST http://localhost:8000/api/v1/comments/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { likeComment(commentId: \"b529ea5d-0410-48cb-813a-1a25d43b6a2c\", userId: \"bc90e095-837e-40f7-9226-a1fa587626eb\") { commentId likeCount } }"
}'
```

### Unlike Comment
```bash
curl -X POST http://localhost:8000/api/v1/comments/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { unlikeComment(commentId: \"b529ea5d-0410-48cb-813a-1a25d43b6a2c\", userId: \"bc90e095-837e-40f7-9226-a1fa587626eb\") { commentId likeCount } }"
}'
```

## Posts Service Collection

### Create Post
```bash
curl -X POST http://localhost:8000/api/v1/posts/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { createPost(userId: \"5807b553-ff97-48ba-88a9-6f3f69395667\", title: \"My First Post\", content: \"This is the content\") { postId title content } }"
}'
```

### Get Post
```bash
curl -X POST http://localhost:8000/api/v1/posts/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "query { post(postId: \"1\") { postId title content } }"
}'
```

### Get Posts by User
```bash
curl -X POST http://localhost:8000/api/v1/posts/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "query { postsByUser(userId: \"5807b553-ff97-48ba-88a9-6f3f69395667\") { postId title content createdAt updatedAt likeCount commentCount } }"
}'
```

### Update Post
```bash
curl -X POST http://localhost:8000/api/v1/posts/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { updatePost(postId: \"1\", title: \"Updated Title\", content: \"Updated content\") { postId title content updatedAt } }"
}'
```

### Delete Post
```bash
curl -X POST http://localhost:8000/api/v1/posts/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { deletePost(postId: \"1\") }"
}'
```

### Like Post
```bash
curl -X POST http://localhost:8000/api/v1/posts/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { likePost(postId: \"1\", userId: \"5807b553-ff97-48ba-88a9-6f3f69395667\") { postId likeCount } }"
}'
```

### Unlike Post
```bash
curl -X POST http://localhost:8000/api/v1/posts/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { unlikePost(postId: \"1\", userId: \"5807b553-ff97-48ba-88a9-6f3f69395667\") { postId likeCount } }"
}'
```

## Property Service Collection

### Create Property
```bash
curl -X POST http://localhost:8000/api/v1/properties/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { createProperty(userId: \"5807b553-ff97-48ba-88a9-6f3f69395667\", title: \"Modern Villa with Pool\", description: \"Beautiful modern villa with swimming pool\", price: 750000.0, location: \"Miami Beach\", propertyType: VILLA, status: ACTIVE, bedrooms: 4, bathrooms: 3, area: 3000.0, yearBuilt: 2022, images: [\"image1.jpg\", \"image2.jpg\"], amenities: [\"Pool\", \"Garden\", \"Garage\"], latitude: 25.7617, longitude: -80.1918, address: \"123 Palm Avenue\", city: \"Miami\", state: \"Florida\", country: \"USA\", zipCode: \"33139\") { propertyId title price location propertyType status bedrooms bathrooms area } }"
}'
```

### Get Property
```bash
curl -X POST http://localhost:8000/api/v1/properties/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "query { property(propertyId: \"123e4567-e89b-12d3-a456-426614174000\") { propertyId userId title description price location propertyType status bedrooms bathrooms area yearBuilt images amenities createdAt updatedAt viewCount latitude longitude address city state country zipCode } }"
}'
```

### Search Properties
```bash
curl -X POST http://localhost:8000/api/v1/properties/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "query { searchProperties(query: \"beach view\", propertyType: VILLA, minPrice: 500000, maxPrice: 1000000, location: \"Miami\", minBedrooms: 3, minBathrooms: 2, minArea: 2000, maxArea: 5000) { propertyId title price location propertyType bedrooms bathrooms area } }"
}'
```

### Update Property
```bash
curl -X POST http://localhost:8000/api/v1/properties/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { updateProperty(propertyId: \"123e4567-e89b-12d3-a456-426614174000\", title: \"Updated Villa Title\", description: \"Updated description\", price: 800000.0, status: ACTIVE) { propertyId title description price status updatedAt } }"
}'
```

### Delete Property
```bash
curl -X POST http://localhost:8000/api/v1/properties/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { deleteProperty(propertyId: \"123e4567-e89b-12d3-a456-426614174000\") }"
}'
```

### Increment View Count
```bash
curl -X POST http://localhost:8000/api/v1/properties/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation { incrementViewCount(propertyId: \"123e4567-e89b-12d3-a456-426614174000\") { propertyId viewCount } }"
}'
```

## Importing to Postman

1. Create a new collection for each service (Users, Comments, Posts, Properties)
2. For each endpoint:
   - Create a new request
   - Set method to POST
   - Set URL to the appropriate endpoint
   - Add header: `Content-Type: application/json`
   - In the Body tab, select "raw" and "JSON"
   - Copy the query from the curl command's -d parameter
   - Save the request

## Environment Variables

Consider setting up environment variables in Postman for:
- `baseUrl`: http://localhost:8000
- `userId`: Your test user ID
- `postId`: Your test post ID
- `commentId`: Your test comment ID
- `propertyId`: Your test property ID 
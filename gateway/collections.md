# API Collections

This document contains all the API endpoints organized by service. Each request includes a cURL command that can be imported into Postman.

## Auth Service Collection

### 1. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation Login { login(email: \"user@example.com\", password: \"yourpassword\") { success token refreshToken message userInfo { id firstName lastName email phone profilePhoto role address latitude longitude bio isactive emailVerified phoneVerified createdAt } } }"
}'
```

Example Response:
```json
{
  "data": {
    "login": {
      "success": true,
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "message": "Login successful",
      "userInfo": {
        "id": 1,
        "firstName": "John",
        "lastName": "Doe",
        "email": "user@example.com",
        "phone": "+1234567890",
        "profilePhoto": null,
        "role": "user",
        "address": "123 Main St",
        "latitude": 12.345678,
        "longitude": 45.678901,
        "bio": "Software Developer",
        "isactive": true,
        "emailVerified": true,
        "phoneVerified": false,
        "createdAt": "2024-02-26T12:00:00Z"
      }
    }
  }
}
```

### 2. Send OTP

a) For Email Verification:
```bash
curl -X POST http://localhost:8000/api/v1/auth/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation SendVerificationOTP { sendOtp(email: \"user@example.com\", type: VERIFICATION) { success message channels } }"
}'
```

b) For Password Reset:
```bash
curl -X POST http://localhost:8000/api/v1/auth/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation SendPasswordResetOTP { sendOtp(email: \"user@example.com\", type: PASSWORD_RESET) { success message channels } }"
}'
```

c) For Login OTP:
```bash
curl -X POST http://localhost:8000/api/v1/auth/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation SendLoginOTP { sendOtp(email: \"user@example.com\", type: LOGIN) { success message channels } }"
}'
```

Example Response:
```json
{
  "data": {
    "sendOtp": {
      "success": true,
      "message": "OTP sent successfully via email",
      "channels": ["email"]
    }
  }
}
```

### 3. Verify OTP

a) Verify Email:
```bash
curl -X POST http://localhost:8000/api/v1/auth/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation VerifyEmailOTP { verifyOtp(email: \"user@example.com\", otpCode: \"123456\", type: VERIFICATION) { success message userInfo { email emailVerified } } }"
}'
```

b) Verify Password Reset OTP:
```bash
curl -X POST http://localhost:8000/api/v1/auth/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation VerifyPasswordResetOTP { verifyOtp(email: \"user@example.com\", otpCode: \"123456\", type: PASSWORD_RESET) { success message userInfo { email emailVerified } } }"
}'
```

c) Verify Login OTP:
```bash
curl -X POST http://localhost:8000/api/v1/auth/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation VerifyLoginOTP { verifyOtp(email: \"user@example.com\", otpCode: \"123456\", type: LOGIN) { success token message userInfo { id email emailVerified } } }"
}'
```

Example Response:
```json
{
  "data": {
    "verifyOtp": {
      "success": true,
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "message": "OTP verified successfully",
      "userInfo": {
        "id": 1,
        "email": "user@example.com",
        "emailVerified": true
      }
    }
  }
}
```

### 4. Password Reset Flow

1. Request Password Reset OTP:
```bash
curl -X POST http://localhost:8000/api/v1/auth/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation RequestPasswordReset { sendOtp(email: \"user@example.com\", type: PASSWORD_RESET) { success message channels } }"
}'
```

2. Reset Password with OTP:
```bash
curl -X POST http://localhost:8000/api/v1/auth/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation ResetPassword { resetPassword(email: \"user@example.com\", otpCode: \"123456\", newPassword: \"newSecurePassword123\", confirmPassword: \"newSecurePassword123\") { success message userInfo { email emailVerified } } }"
}'
```

Example Response:
```json
{
  "data": {
    "resetPassword": {
      "success": true,
      "message": "Password reset successful",
      "userInfo": {
        "email": "user@example.com",
        "emailVerified": true
      }
    }
  }
}
```

### Error Responses

1. User Not Found:
```json
{
  "errors": [{
    "message": "User not found",
    "path": ["sendOtp"]
  }]
}
```

2. Invalid OTP:
```json
{
  "errors": [{
    "message": "Invalid OTP",
    "path": ["verifyOtp"]
  }]
}
```

3. OTP Expired:
```json
{
  "errors": [{
    "message": "OTP expired or not found",
    "path": ["verifyOtp"]
  }]
}
```

4. Invalid Credentials:
```json
{
  "errors": [{
    "message": "Invalid credentials",
    "path": ["login"]
  }]
}
```

5. Password Mismatch:
```json
{
  "errors": [{
    "message": "Passwords do not match",
    "path": ["resetPassword"]
  }]
}
```

## User Service Collection

### 1. Create User
```bash
curl -X POST http://localhost:8000/api/v1/users/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation CreateUser { createUser(firstName: \"John\", lastName: \"Doe\", email: \"john@example.com\", phone: \"+1234567890\", password: \"securepassword123\", role: \"user\", address: \"123 Main St\", latitude: 12.345678, longitude: 45.678901, bio: \"Software Developer\") { id firstName lastName email phone profilePhoto role address latitude longitude bio isactive emailVerified phoneVerified createdAt } }"
}'
```

Example Response:
```json
{
  "data": {
    "createUser": {
      "id": 1,
      "firstName": "John",
      "lastName": "Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "profilePhoto": null,
      "role": "user",
      "address": "123 Main St",
      "latitude": 12.345678,
      "longitude": 45.678901,
      "bio": "Software Developer",
      "isactive": true,
      "emailVerified": false,
      "phoneVerified": false,
      "createdAt": "2024-02-26T12:00:00Z"
    }
  }
}
```

### 2. Get User
```bash
curl -X POST http://localhost:8000/api/v1/users/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "query GetUser { user(id: 1) { id firstName lastName email phone profilePhoto role address latitude longitude bio isactive emailVerified phoneVerified createdAt ratings { id ratedUserId ratedByUserId ratingValue review ratingType createdAt updatedAt } followersCount followingCount } }"
}'
```

Example Response:
```json
{
  "data": {
    "user": {
      "id": 1,
      "firstName": "John",
      "lastName": "Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "profilePhoto": null,
      "role": "user",
      "address": "123 Main St",
      "latitude": 12.345678,
      "longitude": 45.678901,
      "bio": "Software Developer",
      "isactive": true,
      "emailVerified": false,
      "phoneVerified": false,
      "createdAt": "2024-02-26T12:00:00Z",
      "ratings": [],
      "followersCount": 0,
      "followingCount": 0
    }
  }
}
```

### 3. Create User Rating
```bash
curl -X POST http://localhost:8000/api/v1/users/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation CreateUserRating { createUserRating(ratedUserId: 2, ratedByUserId: 1, ratingValue: 5, review: \"Excellent service!\", ratingType: \"PROFESSIONAL\") { id ratedUserId ratedByUserId ratingValue review ratingType createdAt updatedAt } }"
}'
```

Example Response:
```json
{
  "data": {
    "createUserRating": {
      "id": 1,
      "ratedUserId": 2,
      "ratedByUserId": 1,
      "ratingValue": 5,
      "review": "Excellent service!",
      "ratingType": "PROFESSIONAL",
      "createdAt": "2024-02-26T12:00:00Z",
      "updatedAt": "2024-02-26T12:00:00Z"
    }
  }
}
```

### 4. Get User Ratings
```bash
curl -X POST http://localhost:8000/api/v1/users/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "query GetUserRatings { userRatings(userId: 1) { id ratedUserId ratedByUserId ratingValue review ratingType createdAt updatedAt } }"
}'
```

### 5. Follow User
```bash
curl -X POST http://localhost:8000/api/v1/users/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "mutation FollowUser { followUser(userId: 1, followingId: 2) { id userId followingId status followedAt } }"
}'
```

### 6. Get User Followers
```bash
curl -X POST http://localhost:8000/api/v1/users/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "query GetUserFollowers { userFollowers(userId: 1) { id userId followingId status followedAt } }"
}'
```

### 7. Get User Following
```bash
curl -X POST http://localhost:8000/api/v1/users/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "query GetUserFollowing { userFollowing(userId: 1) { id userId followingId status followedAt } }"
}'
```

### 8. Check Following Status
```bash
curl -X POST http://localhost:8000/api/v1/users/graphql \
-H "Content-Type: application/json" \
-d '{
  "query": "query CheckFollowingStatus { checkFollowingStatus(userId: 1, followingId: 2) { id userId followingId status followedAt } }"
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
### Auth Service (gRPC)

- Login
```json
Request (auth.LoginRequest):
{ "email": "user@example.com", "password": "Passw0rd!" }

Response (auth.LoginResponse):
{ "token": "<JWT>", "refresh_token": "<JWT>",
  "user_info": { "id": 1, "first_name": "Ram", "email": "user@example.com", "profile_photo_id": 101, "cover_photo_id": 202 }
}
```

- ValidateToken
```json
Request (auth.ValidateTokenRequest):
{ "token": "<JWT>" }

Response (auth.ValidateTokenResponse):
{ "valid": true, "message": "Token is valid",
  "user_info": { "id": 1, "first_name": "Ram", "email": "user@example.com" }
}
```

- SendOTP / VerifyOTP
```json
Request (auth.OTPRequest):
{ "email": "user@example.com", "phone": "", "type": "PASSWORD_RESET" }
Response (auth.OTPResponse):
{ "success": true, "message": "OTP sent successfully", "channels": ["email"] }

Request (auth.VerifyOTPRequest):
{ "email": "user@example.com", "otp_code": "123456", "type": "PASSWORD_RESET" }
Response (auth.VerifyOTPResponse):
{ "success": true, "message": "OTP verified, proceed with password reset", "token": "" }
```

- ForgotPassword / ResetPassword
```json
Request (auth.ForgotPasswordRequest):
{ "email": "user@example.com" }
Response (auth.ForgotPasswordResponse):
{ "success": true, "message": "Reset instructions sent via email", "channels": ["email"] }

Request (auth.ResetPasswordRequest):
{ "email": "user@example.com", "otp_code": "123456", "new_password": "NewPass!1", "confirm_password": "NewPass!1" }
Response (auth.ResetPasswordResponse):
{ "success": true, "message": "Password reset successful" }
```

- Logout
```json
Request (auth.LogoutRequest):
{ "token": "<access>", "refresh_token": "<refresh>" }
Response (auth.LogoutResponse):
{ "success": true, "message": "Logged out successfully" }
```

---

### Gateway GraphQL - User

- Query: user
```graphql
query GetUser($id: Int!) {
  user(id: $id) {
    id first_name last_name email profile_photo_id cover_photo_id isactive created_at
    followers_count following_count
  }
}
```
Variables:
```json
{ "id": 1 }
```

- Mutation: create_user
```graphql
mutation CreateUser($input: CreateUserInput!) {
  create_user(
    first_name: $input.firstName, last_name: $input.lastName,
    email: $input.email, phone: $input.phone, password: $input.password,
    role: $input.role, address: $input.address, latitude: $input.latitude,
    longitude: $input.longitude, bio: $input.bio
  ) { id email created_at }
}
```

- Mutation: updateProfilePhoto (file path)
```graphql
mutation UpdateProfile($userId: Int!, $filePath: String!) {
  updateProfilePhoto(userId: $userId, filePath: $filePath, fileName: "avatar.jpg", contentType: "image/jpeg") {
    id profile_photo_id
  }
}
```

- Mutation: updateCoverPhoto (file path)
```graphql
mutation UpdateCover($userId: Int!, $filePath: String!) {
  updateCoverPhoto(userId: $userId, filePath: $filePath, fileName: "cover.jpg", contentType: "image/jpeg") {
    id cover_photo_id
  }
}
```

- Query: media by id
```graphql
query Media($mediaId: Int!) {
  media(mediaId: $mediaId) { id media_url media_type uploaded_at }
}
```

- Mutation: create_user_rating
```graphql
mutation RateUser($input: RateUserInput!) {
  create_user_rating(
    rated_user_id: $input.ratedUserId,
    rated_by_user_id: $input.ratedByUserId,
    rating_value: $input.ratingValue,
    title: $input.title,
    review: $input.review,
    rating_type: $input.ratingType,
    is_anonymous: $input.isAnonymous
  ) { id rated_user_id rated_by_user_id rating_value title review created_at }
}
```

- Mutation: follow_user
```graphql
mutation Follow($userId: Int!, $followingId: Int!) {
  follow_user(user_id: $userId, following_id: $followingId) {
    id follower_id following_id status followed_at
  }
}
```

- Query: user_followers / user_following
```graphql
query Followers($userId: Int!) {
  user_followers(user_id: $userId) { id follower_id following_id status followed_at }
}

query Following($userId: Int!) {
  user_following(user_id: $userId) { id follower_id following_id status followed_at }
}
```

- Query: check_following_status
```graphql
query CheckFollow($userId: Int!, $followingId: Int!) {
  check_following_status(user_id: $userId, following_id: $followingId) {
    id follower_id following_id status followed_at
  }
}
```

---

### Gateway GraphQL - Posts

- Mutation: createPost (media via filePath)
```graphql
mutation CreatePost($input: CreatePostInput!) {
  createPost(
    userId: $input.userId,
    title: $input.title,
    content: $input.content,
    visibility: $input.visibility,
    propertyType: $input.type,
    location: $input.location,
    mapLocation: $input.mapLocation,
    price: $input.price,
    status: $input.status,
    media: $input.media
  ) {
    success message
    post { id title mapLocation createdAt media { id mediaUrl mediaType } }
  }
}
```
Variables:
```json
{
  "input": {
    "userId": 1,
    "title": "2 BHK Apartment",
    "content": "Nice flat",
    "visibility": "public",
    "type": "RESIDENTIAL",
    "location": "Noida",
    "mapLocation": "28.614,77.362",
    "price": 7500000,
    "status": "active",
    "media": [
      { "mediaType": "image", "mediaOrder": 1, "caption": "Front", "filePath": "C:/tmp/front.jpg", "fileName": "front.jpg", "contentType": "image/jpeg" }
    ]
  }
}
```

- Mutation: addPostMedia (filePath)
```graphql
mutation AddMedia($postId: Int!, $media: [PostMediaInput!]!) {
  addPostMedia(postId: $postId, media: $media) {
    success message
    post { id media { id mediaUrl mediaType mediaOrder } }
  }
}
```
Variables:
```json
{
  "postId": 10,
  "media": [
    { "mediaType": "image", "mediaOrder": 1, "caption": "Hall", "filePath": "C:/tmp/hall.jpg", "fileName": "hall.jpg", "contentType": "image/jpeg" }
  ]
}
```

- Queries
```graphql
query Post($id: Int!) { post(postId: $id) { id title content media { id mediaUrl } } }
query PostsByUser($uid: Int!) { postsByUser(userId: $uid, page: 1, limit: 10) { id title } }
query SearchPosts { searchPosts(propertyType: "RESIDENTIAL", location: "Noida", page: 1, limit: 10) { id title } }
```

- Query: postComments
```graphql
query PostComments($postId: Int!) {
  postComments(postId: $postId, page: 1, limit: 10) {
    id postId userId userFirstName userLastName comment addedAt
  }
}
```

- Comments & Likes (examples)
```graphql
mutation { createComment(postId: 10, userId: 1, comment: "Nice!") { success message comment { id comment } } }
mutation { updateComment(commentId: 5, comment: "Edited") { success message comment { id comment } } }
mutation { deleteComment(commentId: 5) { success message } }
mutation { likePost(postId: 10, userId: 1) { success message post { id likeCount } } }
mutation { unlikePost(postId: 10, userId: 1) { success message post { id likeCount } } }
```

- Mutations: updatePost / deletePost / deletePostMedia
```graphql
mutation { updatePost(postId: 10, title: "Updated Title", status: "active") { success message post { id title status } } }
mutation { deletePost(postId: 10) { success message post { id } } }
mutation { deletePostMedia(mediaId: 25) { success message } }
```

---

### Gateway GraphQL - Property

- Query: property
```graphql
query GetProperty($id: String!) {
  property(propertyId: $id) { propertyId title price city state country isActive }
}
```

- Query: search_properties
```graphql
query SearchProps {
  search_properties(query: "sector 62", propertyType: APARTMENT, min_price: 1000000, max_price: 8000000) {
    propertyId title price city state
  }
}
```

- Mutation: create_property
```graphql
mutation CreateProperty($p: CreatePropertyInput!) {
  create_property(
    userId: $p.userId, title: $p.title, description: $p.description,
    price: $p.price, location: $p.location, propertyType: $p.propertyType,
    status: $p.status, bedrooms: $p.bedrooms, bathrooms: $p.bathrooms,
    area: $p.area, yearBuilt: $p.yearBuilt, images: $p.images, amenities: $p.amenities,
    latitude: $p.latitude, longitude: $p.longitude, address: $p.address,
    city: $p.city, state: $p.state, country: $p.country, zipCode: $p.zipCode,
    isActive: true
  ) { propertyId title price city state country }
}
```

- Mutations: update_property / delete_property / increment_view_count
```graphql
mutation UpdateProp($id: String!) {
  update_property(
    propertyId: $id,
    title: "New Title",
    price: 9999999
  ) { propertyId title price }
}

mutation DeleteProp($id: String!) { delete_property(propertyId: $id) }

mutation IncViews($id: String!) {
  increment_view_count(propertyId: $id) {
    success message
    property { propertyId viewCount }
  }
}
```

- Ratings & Followers
```graphql
mutation { createPropertyRating(propertyId: 123, ratedByUserId: 1, ratingValue: 5, title: "Great", review: "Nice project", ratingType: "quality") { id propertyId ratingValue title } }
mutation { followProperty(userId: 1, propertyId: 123) { id userId propertyId status } }
query { propertyRatings(propertyId: 123) { id ratingValue title } }
query { propertyFollowers(propertyId: 123) { id userId propertyId status } }
```

- AddPropertyMedia (file path)
```graphql
mutation AddPropertyMedia($propertyId: Int!, $media: [PropertyMediaInput!]!) {
  addPropertyMedia(propertyId: $propertyId, media: $media) {
    success message
    media { id propertyId mediaUrl mediaType mediaOrder }
  }
}
```
Variables:
```json
{
  "propertyId": 123,
  "media": [
    { "filePath": "C:/tmp/property/front.jpg", "mediaType": "image", "mediaOrder": 1, "caption": "Front", "contentType": "image/jpeg" }
  ]
}
```


import grpc
import bcrypt
from concurrent import futures
from app.proto_files import user_pb2, user_pb2_grpc
from app.repository.user_repository import (
    get_user_by_id, create_user, get_user_by_email,
    create_rating, get_ratings,
    create_follower, get_followers, get_following,
    check_following_status, create_media, get_media_by_id
)
from app.interceptors.auth_interceptor import AuthServerInterceptor


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
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone=user.phone,
                role=user.role if user.role else "",
                address=user.address if user.address else "",
                latitude=user.latitude if user.latitude else 0.0,
                longitude=user.longitude if user.longitude else 0.0,
                bio=user.bio if user.bio else "",
                isactive=user.isactive,
                email_verified=user.email_verified,
                phone_verified=user.phone_verified,
                created_at=str(user.created_at) if user.created_at else "",
                gst_no=user.gst_no if user.gst_no else "",
                cover_photo_id=user.cover_photo_id if user.cover_photo_id else 0,
                profile_photo_id=user.profile_photo_id if user.profile_photo_id else 0,
                last_login_at=str(user.last_login_at) if user.last_login_at else ""
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting user: {str(e)}")
            return user_pb2.UserResponse()

    def CreateUser(self, request, context):
        try:
            # Validate required fields
            if not request.first_name or not request.email or not request.password:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("First name, email, and password are required")
                return user_pb2.UserResponse()

            # Check if email already exists
            existing_user = get_user_by_email(request.email)
            if existing_user:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Email already registered")
                return user_pb2.UserResponse()

            # Hash the password
            try:
                hashed_password = bcrypt.hashpw(request.password.encode(), bcrypt.gensalt()).decode('utf-8')
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Error processing password")
                return user_pb2.UserResponse()

            # Create user with hashed password
            user_id = create_user(
                first_name=request.first_name,
                last_name=request.last_name,
                email=request.email,
                phone=request.phone,
                password=hashed_password,
                role=request.role,
                address=request.address,
                latitude=request.latitude,
                longitude=request.longitude,
                bio=request.bio,
                gst_no=request.gst_no,

                cover_photo_id=None if not request.HasField('cover_photo_id') else request.cover_photo_id,
                profile_photo_id=None if not request.HasField('profile_photo_id') else request.profile_photo_id
            )
            
            # Return the created user
            return self.GetUser(user_pb2.UserRequest(id=user_id), context)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating user: {str(e)}")
            return user_pb2.UserResponse()

    def CreateRating(self, request, context):
        try:
            # Validate rating value
            if not 1 <= request.rating_value <= 5:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Rating value must be between 1 and 5")
                return user_pb2.RatingResponse()

            # Check if users exist
            rated_user = get_user_by_id(request.rated_user_id)
            rating_user = get_user_by_id(request.rated_by_user_id)
            
            if not rated_user or not rating_user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("One or both users not found")
                return user_pb2.RatingResponse()

            rating_id = create_user_rating(
                rated_user_id=request.rated_user_id,
                rated_by_user_id=request.rated_by_user_id,
                rating_value=request.rating_value,
                title=request.title,
                review=request.review,
                rating_type=request.rating_type,
                is_anonymous=request.is_anonymous
            )

            # Get the created rating
            ratings = get_user_ratings(request.rated_user_id)
            for rating in ratings:
                if rating.id == rating_id:
                    return user_pb2.RatingResponse(
                        id=rating.id,
                        rated_user_id=rating.rated_user_id,
                        rated_by_user_id=rating.rated_by_user_id,
                        rating_value=rating.rating_value,
                        title=rating.title if rating.title else "",
                        review=rating.review if rating.review else "",
                        rating_type=rating.rating_type if rating.rating_type else "",
                        is_anonymous=rating.is_anonymous,
                        created_at=str(rating.created_at),
                        updated_at=str(rating.updated_at)
                    )

            return user_pb2.RatingResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating rating: {str(e)}")
            return user_pb2.RatingResponse()

    def GetUserRatings(self, request, context):
        try:
            user = get_user_by_id(request.id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.id} not found")
                return user_pb2.UserRatingsResponse()

            ratings = get_user_ratings(request.id)
            rating_responses = []
            for rating in ratings:
                rating_responses.append(user_pb2.RatingResponse(
                    id=rating.id,
                    rated_user_id=rating.rated_user_id,
                    rated_by_user_id=rating.rated_by_user_id,
                    rating_value=rating.rating_value,
                    title=rating.title if rating.title else "",
                    review=rating.review if rating.review else "",
                    rating_type=rating.rating_type if rating.rating_type else "",
                    is_anonymous=rating.is_anonymous,
                    created_at=str(rating.created_at),
                    updated_at=str(rating.updated_at)
                ))

            return user_pb2.RatingsResponse(ratings=rating_responses)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting ratings: {str(e)}")
            return user_pb2.UserRatingsResponse()

    def FollowUser(self, request, context):
        try:
            # Check if users exist
            user = get_user_by_id(request.user_id)
            following = get_user_by_id(request.following_id)
            
            if not user or not following:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("One or both users not found")
                return user_pb2.FollowUserResponse()

            # Check if already following
            existing = check_following_status(request.user_id, request.following_id)
            if existing:
                return user_pb2.FollowUserResponse(
                    id=existing.id,
                    user_id=existing.user_id,
                    following_id=existing.following_id,
                    status=existing.status,
                    followed_at=str(existing.followed_at)
                )

            follower_id = create_user_follower(
                user_id=request.user_id,
                following_id=request.following_id
            )

            # Get the created follower relationship
            follower = check_following_status(request.user_id, request.following_id)
            if follower:
                return user_pb2.FollowUserResponse(
                    id=follower.id,
                    user_id=follower.user_id,
                    following_id=follower.following_id,
                    status=follower.status,
                    followed_at=str(follower.followed_at)
                )

            return user_pb2.FollowUserResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error following user: {str(e)}")
            return user_pb2.FollowUserResponse()

    def GetUserFollowers(self, request, context):
        try:
            user = get_user_by_id(request.id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.id} not found")
                return user_pb2.UserFollowersResponse()

            followers = get_user_followers(request.id)
            follower_responses = []
            for follower in followers:
                follower_responses.append(user_pb2.FollowUserResponse(
                    id=follower.id,
                    user_id=follower.user_id,
                    following_id=follower.following_id,
                    status=follower.status,
                    followed_at=str(follower.followed_at)
                ))

            return user_pb2.UserFollowersResponse(followers=follower_responses)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting followers: {str(e)}")
            return user_pb2.UserFollowersResponse()

    def GetUserFollowing(self, request, context):
        try:
            user = get_user_by_id(request.id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.id} not found")
                return user_pb2.UserFollowersResponse()

            following = get_user_following(request.id)
            following_responses = []
            for follow in following:
                following_responses.append(user_pb2.FollowUserResponse(
                    id=follow.id,
                    user_id=follow.user_id,
                    following_id=follow.following_id,
                    status=follow.status,
                    followed_at=str(follow.followed_at)
                ))

            return user_pb2.UserFollowersResponse(followers=following_responses)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting following: {str(e)}")
            return user_pb2.UserFollowersResponse()

    def CheckFollowingStatus(self, request, context):
        try:
            # First check if both users exist
            user = get_user_by_id(request.user_id)
            following_user = get_user_by_id(request.following_id)
            
            if not user or not following_user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("One or both users not found")
                return user_pb2.FollowUserResponse()

            # Check following status
            status = check_following_status(request.user_id, request.following_id)
            if not status:
                # Return empty response with NOT_FOUND status if no following relationship exists
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("No following relationship found")
                return user_pb2.FollowUserResponse()

            return user_pb2.FollowUserResponse(
                id=status.id,
                user_id=status.user_id,
                following_id=status.following_id,
                status=status.status if status.status else "",
                followed_at=str(status.followed_at) if status.followed_at else ""
            )
        except Exception as e:
            print(f"Error checking following status: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error checking following status: {str(e)}")
            return user_pb2.FollowUserResponse()

    def UploadMedia(self, request, context):
        try:
            # Validate required fields
            if not request.media_type or not request.media_url:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Media type and URL are required")
                return user_pb2.MediaResponse()

            # Validate media type
            valid_media_types = ['image', 'video']
            if request.media_type not in valid_media_types:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(f"Media type must be one of: {', '.join(valid_media_types)}")
                return user_pb2.MediaResponse()

            # Create media record
            media_id = create_media(
                context_id=request.context_id,
                context_type=request.context_type,
                media_type=request.media_type,
                media_url=request.media_url,
                media_order=request.media_order,
                media_size=request.media_size,
                caption=request.caption
            )

            # Get and return the created media
            media = get_media_by_id(media_id)
            if media:
                return user_pb2.MediaResponse(
                    id=media.id,
                    context_id=media.context_id,
                    context_type=media.context_type,
                    media_type=media.media_type,
                    media_url=media.media_url,
                    media_order=media.media_order,
                    media_size=media.media_size,
                    caption=media.caption if media.caption else "",
                    uploaded_at=str(media.uploaded_at)
                )

            return user_pb2.MediaResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error uploading media: {str(e)}")
            return user_pb2.MediaResponse()

    def GetMedia(self, request, context):
        try:
            media = get_media_by_id(request.id)
            if not media:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Media with ID {request.id} not found")
                return user_pb2.MediaResponse()

            return user_pb2.MediaResponse(
                id=media.id,
                context_id=media.context_id,
                context_type=media.context_type,
                media_type=media.media_type,
                media_url=media.media_url,
                media_order=media.media_order,
                media_size=media.media_size,
                caption=media.caption if media.caption else "",
                uploaded_at=str(media.uploaded_at)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting media: {str(e)}")
            return user_pb2.MediaResponse()

    def UpdateProfilePhoto(self, request, context):
        try:
            # First upload the media
            media_request = request.media
            media_request.context_type = 'user_profile'  # Force context type for profile photo
            
            # Create media record
            media_id = create_media(
                context_id=request.user_id,  # Use user_id as context_id
                context_type='user_profile',
                media_type=media_request.media_type,
                media_url=media_request.media_url,
                media_order=media_request.media_order,
                media_size=media_request.media_size,
                caption=media_request.caption
            )

            if not media_id:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to create media record")
                return user_pb2.UserResponse()

            # Update user's profile photo ID
            success = update_user_photo(request.user_id, media_id, is_profile_photo=True)
            if not success:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to update user's profile photo")
                return user_pb2.UserResponse()

            # Return updated user
            return self.GetUser(user_pb2.UserRequest(id=request.user_id), context)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error updating profile photo: {str(e)}")
            return user_pb2.UserResponse()

    def UpdateCoverPhoto(self, request, context):
        try:
            # First upload the media
            media_request = request.media
            media_request.context_type = 'user_cover'  # Force context type for cover photo
            
            # Create media record
            media_id = create_media(
                context_id=request.user_id,  # Use user_id as context_id
                context_type='user_cover',
                media_type=media_request.media_type,
                media_url=media_request.media_url,
                media_order=media_request.media_order,
                media_size=media_request.media_size,
                caption=media_request.caption
            )

            if not media_id:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to create media record")
                return user_pb2.UserResponse()

            # Update user's cover photo ID
            success = update_user_photo(request.user_id, media_id, is_profile_photo=False)
            if not success:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to update user's cover photo")
                return user_pb2.UserResponse()

            # Return updated user
            return self.GetUser(user_pb2.UserRequest(id=request.user_id), context)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error updating cover photo: {str(e)}")
            return user_pb2.UserResponse()

def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[AuthServerInterceptor()]
    )
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port('localhost:50051')
    print("Starting user service on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
import grpc
import bcrypt
from concurrent import futures
from app.proto_files import user_pb2, user_pb2_grpc
from app.repository.user_repository import (
    get_user_by_id, create_user, get_user_by_email,
    create_rating, get_ratings,
    create_follower, get_followers, get_following, get_pending_follow_requests,
    check_following_status, create_media, get_media_by_id, update_user_photo,
    get_latest_media_for_user_context, update_user_location,
    update_follow_status,
)
from app.interceptors.auth_interceptor import AuthServerInterceptor
from app.utils.s3_utils import (
    upload_file_to_s3,
    build_user_profile_key,
    build_user_cover_key,
)


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

            rating_id = create_rating(
                rated_user_id=request.rated_user_id,
                rated_by_user_id=request.rated_by_user_id,
                rating_value=request.rating_value,
                title=request.title,
                review=request.review,
                rating_type=request.rating_type,
                is_anonymous=request.is_anonymous
            )

            # Get the created rating
            ratings = get_ratings(request.rated_user_id)
            for rating in ratings:
                if rating.id == rating_id:
                    return user_pb2.RatingResponse(
                        id=rating.id,
                        rated_user_id=rating.rated_id,
                        rated_by_user_id=rating.rated_by,
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
                return user_pb2.RatingsResponse()

            ratings = get_ratings(request.id)
            rating_responses = []
            for rating in ratings:
                rating_responses.append(user_pb2.RatingResponse(
                    id=rating.id,
                    rated_user_id=rating.rated_id,
                    rated_by_user_id=rating.rated_by,
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
            return user_pb2.RatingsResponse()

    def FollowUser(self, request, context):
        try:
            # Check if users exist
            follower_user = get_user_by_id(request.follower_id)
            following_user = get_user_by_id(request.following_id)
            
            if not follower_user or not following_user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("One or both users not found")
                return user_pb2.FollowUserResponse()

            # Check if already following
            existing = check_following_status(request.follower_id, request.following_id)
            if existing:
                return user_pb2.FollowUserResponse(
                    id=existing.id,
                    follower_id=existing.follower_id,
                    following_id=existing.following_id,
                    followee_type=existing.followee_type if existing.followee_type else "user",
                    status=existing.status if existing.status else "",
                    followed_at=str(existing.followed_at)
                )

            # Create follow with default 'pending' status if not provided
            follower_row_id = create_follower(
                follower_id=request.follower_id,
                following_id=request.following_id,
                followee_type=request.followee_type if request.followee_type else 'user',
                status=request.status if request.status else 'pending'
            )

            # Get the created follower relationship
            follower = check_following_status(request.follower_id, request.following_id)
            if follower:
                return user_pb2.FollowUserResponse(
                    id=follower.id,
                    follower_id=follower.follower_id,
                    following_id=follower.following_id,
                    followee_type=follower.followee_type if follower.followee_type else "user",
                    status=follower.status if follower.status else "",
                    followed_at=str(follower.followed_at)
                )

            return user_pb2.FollowUserResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error following user: {str(e)}")
            return user_pb2.FollowUserResponse()

    def UpdateFollowStatus(self, request, context):
        try:
            # Only the target user (being followed) should be able to accept/reject
            # We expect request.following_id is the target user, request.follower_id is requester
            updated = update_follow_status(
                follower_id=request.follower_id,
                following_id=request.following_id,
                status=request.status or 'pending',
            )
            if not updated:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Follow relationship not found or invalid status")
                return user_pb2.FollowUserResponse()

            return user_pb2.FollowUserResponse(
                id=updated.id,
                follower_id=updated.follower_id,
                following_id=updated.following_id,
                followee_type=updated.followee_type if updated.followee_type else "user",
                status=updated.status if updated.status else "",
                followed_at=str(updated.followed_at) if updated.followed_at else "",
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error updating follow status: {str(e)}")
            return user_pb2.FollowUserResponse()

    def GetUserFollowers(self, request, context):
        try:
            user = get_user_by_id(request.id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.id} not found")
                return user_pb2.UserFollowersResponse()

            followers = get_followers(request.id)
            follower_responses = []
            for follower in followers:
                follower_responses.append(user_pb2.FollowUserResponse(
                    id=follower.id,
                    follower_id=follower.follower_id,
                    following_id=follower.following_id,
                    followee_type=follower.followee_type if follower.followee_type else "user",
                    status=follower.status if follower.status else "",
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

            following = get_following(request.id)
            following_responses = []
            for follow in following:
                following_responses.append(user_pb2.FollowUserResponse(
                    id=follow.id,
                    follower_id=follow.follower_id,
                    following_id=follow.following_id,
                    followee_type=follow.followee_type if follow.followee_type else "user",
                    status=follow.status if follow.status else "",
                    followed_at=str(follow.followed_at)
                ))

            return user_pb2.UserFollowersResponse(followers=following_responses)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting following: {str(e)}")
            return user_pb2.UserFollowersResponse()

    def GetPendingFollowRequests(self, request, context):
        try:
            user = get_user_by_id(request.id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.id} not found")
                return user_pb2.UserFollowersResponse()

            pending = get_pending_follow_requests(request.id)
            responses = []
            for f in pending:
                responses.append(user_pb2.FollowUserResponse(
                    id=f.id,
                    follower_id=f.follower_id,
                    following_id=f.following_id,
                    followee_type=f.followee_type if f.followee_type else "user",
                    status=f.status if f.status else "",
                    followed_at=str(f.followed_at)
                ))
            return user_pb2.UserFollowersResponse(followers=responses)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting pending follow requests: {str(e)}")
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
                follower_id=status.follower_id,
                following_id=status.following_id,
                status=status.status if status.status else "",
                followed_at=str(status.followed_at) if status.followed_at else ""
            )
        except Exception as e:
            print(f"Error checking following status: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error checking following status: {str(e)}")
            return user_pb2.FollowUserResponse()

    

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
            media_request = request.media
            if not getattr(media_request, 'file_path', None):
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("file_path is required for profile photo upload")
                return user_pb2.UserResponse()

            # Build S3 key and upload
            key = build_user_profile_key(
                request.user_id,
                getattr(media_request, "file_name", None),
                getattr(media_request, "content_type", None),
            )
            public_url, size_bytes = upload_file_to_s3(
                file_path=media_request.file_path,
                key=key,
                content_type=getattr(media_request, "content_type", None),
            )

            # Create media record with S3 URL
            media_id = create_media(
                context_id=request.user_id,
                context_type='user',
                media_type='image',
                media_url=public_url,
                media_order=(media_request.media_order or 1),
                media_size=size_bytes,
                caption=media_request.caption
            )

            if not media_id:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to create media record")
                return user_pb2.UserResponse()

            # Update user's profile photo ID to the latest uploaded media for the user
            latest_media = get_latest_media_for_user_context(request.user_id, 'user')
            effective_media_id = latest_media.id if latest_media else media_id
            success = update_user_photo(request.user_id, effective_media_id, is_profile_photo=True)
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
            media_request = request.media
            if not getattr(media_request, 'file_path', None):
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("file_path is required for cover photo upload")
                return user_pb2.UserResponse()

            # Build S3 key and upload
            key = build_user_cover_key(
                request.user_id,
                getattr(media_request, "file_name", None),
                getattr(media_request, "content_type", None),
            )
            public_url, size_bytes = upload_file_to_s3(
                file_path=media_request.file_path,
                key=key,
                content_type=getattr(media_request, "content_type", None),
            )

            # Create media record with S3 URL
            media_id = create_media(
                context_id=request.user_id,
                context_type='user',
                media_type='image',
                media_url=public_url,
                media_order=(media_request.media_order or 1),
                media_size=size_bytes,
                caption=media_request.caption
            )

            if not media_id:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to create media record")
                return user_pb2.UserResponse()

            # Update user's cover photo ID to the latest uploaded media for the user
            latest_media = get_latest_media_for_user_context(request.user_id, 'user')
            effective_media_id = latest_media.id if latest_media else media_id
            success = update_user_photo(request.user_id, effective_media_id, is_profile_photo=False)
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

    def UpdateUserLocation(self, request, context):
        try:
            if not isinstance(request.user_id, int):
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("user_id must be an integer")
                return user_pb2.UserResponse()
            if request.latitude is None or request.longitude is None:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("latitude and longitude are required")
                return user_pb2.UserResponse()

            user = get_user_by_id(request.user_id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.user_id} not found")
                return user_pb2.UserResponse()

            ok = update_user_location(request.user_id, request.latitude, request.longitude)
            if not ok:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to update user location")
                return user_pb2.UserResponse()

            return self.GetUser(user_pb2.UserRequest(id=request.user_id), context)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error updating user location: {str(e)}")
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
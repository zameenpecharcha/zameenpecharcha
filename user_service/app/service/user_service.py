import grpc
import bcrypt
from concurrent import futures
from app.proto_files import user_pb2, user_pb2_grpc
from app.repository.user_repository import (
    get_user_by_id, create_user, get_user_by_email,
    create_rating, get_ratings,
    create_follower, get_followers, get_following,
    check_following_status, create_media, get_media_by_id, update_user_photo
)
from app.interceptors.auth_interceptor import AuthServerInterceptor
from app.utils.s3_utils import upload_bytes_and_get_url, build_user_media_key, get_bucket_name, verify_s3_connection
from app.utils.log_utils import log_msg


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
                return user_pb2.RatingsResponse()

            ratings = get_ratings(request.id)
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
                    followee_type=existing.followee_type if existing.followee_type else "",
                    status=existing.status if existing.status else "",
                    followed_at=str(existing.followed_at)
                )

            follower_row_id = create_follower(
                follower_id=request.follower_id,
                following_id=request.following_id,
                followee_type=request.followee_type if request.followee_type else None,
                status=request.status if request.status else 'active'
            )

            # Get the created follower relationship
            follower = check_following_status(request.follower_id, request.following_id)
            if follower:
                return user_pb2.FollowUserResponse(
                    id=follower.id,
                    follower_id=follower.follower_id,
                    following_id=follower.following_id,
                    followee_type=follower.followee_type if follower.followee_type else "",
                    status=follower.status if follower.status else "",
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

            followers = get_followers(request.id)
            follower_responses = []
            for follower in followers:
                follower_responses.append(user_pb2.FollowUserResponse(
                    id=follower.id,
                    follower_id=follower.follower_id,
                    following_id=follower.following_id,
                    followee_type=follower.followee_type if follower.followee_type else "",
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
                    followee_type=follow.followee_type if follow.followee_type else "",
                    status=follow.status if follow.status else "",
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
            user = get_user_by_id(request.follower_id)
            following_user = get_user_by_id(request.following_id)
            
            if not user or not following_user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("One or both users not found")
                return user_pb2.FollowUserResponse()

            # Check following status
            status = check_following_status(request.follower_id, request.following_id)
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

    def UploadMedia(self, request, context):
        print("=== Raw Request Debug ===")
        print(f"Request type: {type(request)}")
        print(f"Request dict: {request.__dict__}")
        print("=== Request Fields ===")
        print(f"context_id: {request.context_id}")
        print(f"context_type: {request.context_type!r}")
        print(f"media_type: {request.media_type!r}")
        print(f"file_name: {request.file_name!r}")
        print(f"content_type: {request.content_type!r}")
        print(f"file_content length: {len(request.file_content) if request.file_content else 0}")
        print(f"caption: {request.caption!r}")
        print("=== End Debug ===")
        try:
            # Validate required fields
            if not request.media_type:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Media type is required")
                return user_pb2.MediaResponse()

            # Require file_content for uploads
            if not request.file_content:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("File content is required for uploads")
                return user_pb2.MediaResponse()

            # Validate media type
            valid_media_types = ['image', 'video']
            if request.media_type not in valid_media_types:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(f"Media type must be one of: {', '.join(valid_media_types)}")
                return user_pb2.MediaResponse()

            # Prepare for S3 upload
            media_url = request.media_url
            log_msg("info", f"[MEDIA] Starting media upload. Context: {request.context_type}, Type: {request.media_type}")
            log_msg("info", f"[MEDIA] File content present: {bool(request.file_content)}, Content length: {len(request.file_content) if request.file_content else 0}")
            log_msg("info", f"[MEDIA] File name: {request.file_name}, Content type: {request.content_type}")
            
            # Upload to S3
            bucket = get_bucket_name()
            log_msg("info", f"[DEBUG] Got bucket name: '{bucket}'")
            if not bucket:
                raise ValueError("Missing AWS_S3_BUCKET_NAME env var")
            
            # Verify bucket access once per request
            log_msg("info", "[DEBUG] Attempting to verify S3 connection...")
            if not verify_s3_connection(bucket):
                raise ValueError("Cannot access S3 bucket. Check credentials/permissions.")
            
            # Build S3 key under user/{context_id}/...
            file_name = request.file_name if request.file_name else 'upload.bin'
            if (request.context_type or '').lower() in ['profile photo', 'profile_photo', 'user_profile']:
                key = build_user_media_key(request.context_id, is_profile=True, file_name=file_name)
            elif (request.context_type or '').lower() in ['cover photo', 'cover_photo', 'user_cover']:
                key = build_user_media_key(request.context_id, is_profile=False, file_name=file_name)
            else:
                folder = request.context_type if request.context_type else 'misc'
                key = f"user/{request.context_id}/{folder}/{file_name}"
            
            try:
                uploaded_url = upload_bytes_and_get_url(
                    bucket=bucket,
                    key=key,
                    content_bytes=request.file_content,
                    content_type=request.content_type if request.content_type else 'application/octet-stream'
                )
                media_url = uploaded_url
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"S3 upload failed: {str(e)}")
                return user_pb2.MediaResponse()

            # Create media record
            media_id = create_media(
                context_id=request.context_id,
                context_type=request.context_type,
                media_type=request.media_type,
                media_url=media_url,
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
        print("=== UpdateProfilePhoto Request Debug ===")
        print(f"Request type: {type(request)}")
        print(f"Request dict: {request.__dict__}")
        print("=== Request Fields ===")
        print(f"user_id: {request.user_id}")
        print("Media fields:")
        print(f"  context_id: {request.media.context_id}")
        print(f"  context_type: {request.media.context_type!r}")
        print(f"  media_type: {request.media.media_type!r}")
        print(f"  file_name: {request.media.file_name!r}")
        print(f"  content_type: {request.media.content_type!r}")
        print(f"  file_content length: {len(request.media.file_content) if request.media.file_content else 0}")
        print(f"  caption: {request.media.caption!r}")
        print("=== End Debug ===")
        try:
            # First upload the media
            media_request = request.media
            
            # Require file_content for uploads
            if not media_request.file_content:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("File content is required for profile photo")
                return user_pb2.UserResponse()
                
            # Set default media type if not provided
            if not media_request.media_type:
                media_request.media_type = 'image'

            # Verify user exists
            user = get_user_by_id(request.user_id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.user_id} not found")
                return user_pb2.UserResponse()

            media_request.context_type = 'user_profile'  # Force context type for profile photo
            
            # Prepare for S3 upload
            log_msg("info", f"[PROFILE] Starting profile photo upload for user {request.user_id}")
            log_msg("info", f"[PROFILE] File content present: {bool(media_request.file_content)}, Content length: {len(media_request.file_content) if media_request.file_content else 0}")
            log_msg("info", f"[PROFILE] File name: {media_request.file_name}, Content type: {media_request.content_type}")

            # Upload to S3
            bucket = get_bucket_name()
            log_msg("info", f"[DEBUG] Got bucket name: '{bucket}'")
            if not bucket:
                raise ValueError("Missing AWS_S3_BUCKET_NAME env var")
            
            # Verify bucket access
            log_msg("info", "[DEBUG] Attempting to verify S3 connection...")
            if not verify_s3_connection(bucket):
                raise ValueError("Cannot access S3 bucket. Check credentials/permissions.")

            # Upload file
            key = build_user_media_key(request.user_id, is_profile=True, file_name=(media_request.file_name or 'profile.jpg'))
            try:
                media_url = upload_bytes_and_get_url(
                    bucket=bucket,
                    key=key,
                    content_bytes=media_request.file_content,
                    content_type=media_request.content_type if media_request.content_type else 'image/jpeg'
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"S3 upload failed: {str(e)}")
                return user_pb2.UserResponse()

            # Create media record
            media_id = create_media(
                context_id=request.user_id,  # Use user_id as context_id
                context_type='user_profile',
                media_type=media_request.media_type,
                media_url=media_url,
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
            
            # Upload to S3 if bytes provided
            media_url = media_request.media_url
            if media_request.file_content:
                bucket = get_bucket_name()
                if not bucket:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Missing AWS_S3_BUCKET_NAME env var")
                    return user_pb2.UserResponse()
                if not verify_s3_connection(bucket):
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Cannot access S3 bucket. Check credentials/permissions.")
                    return user_pb2.UserResponse()
                key = build_user_media_key(request.user_id, is_profile=False, file_name=(media_request.file_name or 'cover.jpg'))
                media_url = upload_bytes_and_get_url(
                    bucket=bucket,
                    key=key,
                    content_bytes=media_request.file_content,
                    content_type=media_request.content_type if media_request.content_type else 'image/jpeg'
                )

            # Create media record
            media_id = create_media(
                context_id=request.user_id,  # Use user_id as context_id
                context_type='user_cover',
                media_type=media_request.media_type,
                media_url=media_url,
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
    # Set up logging
    log_msg("info", "Initializing user service...")
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
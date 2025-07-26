import grpc
import bcrypt
from concurrent import futures
from user_service.app.proto_files import user_pb2, user_pb2_grpc
from user_service.app.repository.user_repository import (
    get_user_by_id, create_user, get_user_by_email,
    create_user_rating, get_user_ratings,
    create_user_follower, get_user_followers, get_user_following,
    check_following_status
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
                profile_photo=user.profile_photo if user.profile_photo else "",
                role=user.role if user.role else "",
                address=user.address if user.address else "",
                latitude=user.latitude if user.latitude else 0.0,
                longitude=user.longitude if user.longitude else 0.0,
                bio=user.bio if user.bio else "",
                isActive=user.isactive,
                email_verified=user.email_verified,
                phone_verified=user.phone_verified,
                created_at=str(user.created_at) if user.created_at else ""
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
                bio=request.bio
            )
            
            # Return the created user
            return self.GetUser(user_pb2.UserRequest(id=user_id), context)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating user: {str(e)}")
            return user_pb2.UserResponse()

    def CreateUserRating(self, request, context):
        try:
            # Validate rating value
            if not 1 <= request.rating_value <= 5:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Rating value must be between 1 and 5")
                return user_pb2.UserRatingResponse()

            # Check if users exist
            rated_user = get_user_by_id(request.rated_user_id)
            rating_user = get_user_by_id(request.rated_by_user_id)
            
            if not rated_user or not rating_user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("One or both users not found")
                return user_pb2.UserRatingResponse()

            rating_id = create_user_rating(
                rated_user_id=request.rated_user_id,
                rated_by_user_id=request.rated_by_user_id,
                rating_value=request.rating_value,
                review=request.review,
                rating_type=request.rating_type
            )

            # Get the created rating
            ratings = get_user_ratings(request.rated_user_id)
            for rating in ratings:
                if rating.id == rating_id:
                    return user_pb2.UserRatingResponse(
                        id=rating.id,
                        rated_user_id=rating.rated_user_id,
                        rated_by_user_id=rating.rated_by_user_id,
                        rating_value=rating.rating_value,
                        review=rating.review if rating.review else "",
                        rating_type=rating.rating_type if rating.rating_type else "",
                        created_at=str(rating.created_at),
                        updated_at=str(rating.updated_at)
                    )

            return user_pb2.UserRatingResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating rating: {str(e)}")
            return user_pb2.UserRatingResponse()

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
                rating_responses.append(user_pb2.UserRatingResponse(
                    id=rating.id,
                    rated_user_id=rating.rated_user_id,
                    rated_by_user_id=rating.rated_by_user_id,
                    rating_value=rating.rating_value,
                    review=rating.review if rating.review else "",
                    rating_type=rating.rating_type if rating.rating_type else "",
                    created_at=str(rating.created_at),
                    updated_at=str(rating.updated_at)
                ))

            return user_pb2.UserRatingsResponse(ratings=rating_responses)
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

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')
    print("Starting user service on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
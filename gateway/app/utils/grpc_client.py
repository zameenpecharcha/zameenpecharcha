import grpc
import sys
import os
from pathlib import Path
from app.utils.log_utils import log_msg

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from app.proto_files.auth import auth_pb2_grpc, auth_pb2
from app.proto_files.user import user_pb2_grpc, user_pb2
from app.proto_files.posts import post_pb2_grpc, post_pb2
import app.proto_files.comments.comments_pb2 as comments_pb2
import app.proto_files.comments.comments_pb2_grpc as comments_pb2_grpc
from app.proto_files.property import property_pb2, property_pb2_grpc

class AuthServiceClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50052')
        self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)

    def login(self, email: str, password: str):
        try:
            request = auth_pb2.LoginRequest(
                email=email,
                password=password
            )
            return self.stub.Login(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in login: {str(e)}")
            raise e

    def send_otp(self, email: str, phone: str = None, otp_type: int = 0):
        try:
            request = auth_pb2.OTPRequest(
                email=email,
                phone=phone,
                type=otp_type.value if hasattr(otp_type, 'value') else otp_type
            )
            return self.stub.SendOTP(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in send_otp: {str(e)}")
            raise e

    def verify_otp(self, email: str, otp_code: str, otp_type: int = 0):
        try:
            request = auth_pb2.VerifyOTPRequest(
                email=email,
                otp_code=otp_code,
                type=otp_type.value if hasattr(otp_type, 'value') else otp_type
            )
            return self.stub.VerifyOTP(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in verify_otp: {str(e)}")
            raise e

    def forgot_password(self, email: str, phone: str = None):
        try:
            request = auth_pb2.ForgotPasswordRequest(
                email=email,
                phone=phone
            )
            return self.stub.ForgotPassword(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in forgot_password: {str(e)}")
            raise e

    def reset_password(self, email: str, otp_code: str, new_password: str, confirm_password: str):
        try:
            request = auth_pb2.ResetPasswordRequest(
                email=email,
                otp_code=otp_code,
                new_password=new_password,
                confirm_password=confirm_password
            )
            return self.stub.ResetPassword(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in reset_password: {str(e)}")
            raise e

class UserServiceClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = user_pb2_grpc.UserServiceStub(self.channel)

    def get_user(self, id):
        try:
            request = user_pb2.UserRequest(id=id)
            return self.stub.GetUser(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in get_user: {str(e)}")
            raise e

    def create_user(self, first_name, last_name, email, phone, password, role=None, 
                   address=None, latitude=None, longitude=None, bio=None):
        try:
            request = user_pb2.CreateUserRequest(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                password=password,
                role=role,
                address=address,
                latitude=latitude,
                longitude=longitude,
                bio=bio
            )
            return self.stub.CreateUser(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in create_user: {str(e)}")
            raise e

    def create_user_rating(self, rated_user_id, rated_by_user_id, rating_value, review=None, rating_type=None):
        try:
            request = user_pb2.CreateUserRatingRequest(
                rated_user_id=rated_user_id,
                rated_by_user_id=rated_by_user_id,
                rating_value=rating_value,
                review=review,
                rating_type=rating_type
            )
            return self.stub.CreateUserRating(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in create_user_rating: {str(e)}")
            raise e

    def get_user_ratings(self, user_id):
        try:
            request = user_pb2.UserRequest(id=user_id)
            return self.stub.GetUserRatings(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in get_user_ratings: {str(e)}")
            raise e

    def follow_user(self, user_id, following_id):
        try:
            request = user_pb2.FollowUserRequest(
                user_id=user_id,
                following_id=following_id
            )
            return self.stub.FollowUser(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in follow_user: {str(e)}")
            raise e

    def get_user_followers(self, user_id):
        try:
            request = user_pb2.UserRequest(id=user_id)
            return self.stub.GetUserFollowers(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in get_user_followers: {str(e)}")
            raise e

    def get_user_following(self, user_id):
        try:
            request = user_pb2.UserRequest(id=user_id)
            return self.stub.GetUserFollowing(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in get_user_following: {str(e)}")
            raise e

    def check_following_status(self, user_id, following_id):
        try:
            request = user_pb2.CheckFollowingRequest(
                user_id=user_id,
                following_id=following_id
            )
            return self.stub.CheckFollowingStatus(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in check_following_status: {str(e)}")
            raise e

class CommentsServiceClient:
    def __init__(self, host='localhost', port=50053):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = comments_pb2_grpc.CommentsServiceStub(self.channel)

    def create_comment(self, post_id: str, user_id: str, content: str, parent_comment_id: str = None):
        request = comments_pb2.CommentCreateRequest(
            post_id=post_id,
            user_id=user_id,
            content=content,
            parent_comment_id=parent_comment_id if parent_comment_id else ""
        )
        return self.stub.CreateComment(request)

    def get_comment(self, comment_id: str):
        request = comments_pb2.CommentRequest(comment_id=comment_id)
        return self.stub.GetComment(request)

    def get_comments_by_post(self, post_id: str):
        request = comments_pb2.PostCommentsRequest(post_id=post_id)
        return self.stub.GetCommentsByPost(request)

    def get_replies(self, comment_id: str):
        request = comments_pb2.CommentRequest(comment_id=comment_id)
        return self.stub.GetReplies(request)

    def update_comment(self, comment_id: str, content: str):
        request = comments_pb2.CommentUpdateRequest(
            comment_id=comment_id,
            content=content
        )
        return self.stub.UpdateComment(request)

    def delete_comment(self, comment_id: str):
        request = comments_pb2.CommentRequest(comment_id=comment_id)
        return self.stub.DeleteComment(request)

    def like_comment(self, comment_id: str, user_id: str):
        request = comments_pb2.LikeCommentRequest(
            comment_id=comment_id,
            user_id=user_id
        )
        return self.stub.LikeComment(request)

    def unlike_comment(self, comment_id: str, user_id: str):
        request = comments_pb2.UnlikeCommentRequest(
            comment_id=comment_id,
            user_id=user_id
        )
        return self.stub.UnlikeComment(request)

class PostsServiceClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50053')
        self.stub = post_pb2_grpc.PostsServiceStub(self.channel)

    def create_post(self, user_id: int, title: str, content: str, visibility: str = None,
                   property_type: str = None, location: str = None, map_location: str = None,
                   price: float = None, status: str = None, media=None):
        try:
            request = post_pb2.PostCreateRequest(
                user_id=user_id,
                title=title,
                content=content,
                visibility=visibility,
                property_type=property_type,
                location=location,
                map_location=map_location,
                price=price,
                status=status,
                media=media or []
            )
            return self.stub.CreatePost(request)
        except grpc.RpcError as e:
            log_msg(f"Error in create_post: {str(e)}")
            raise

    def get_post(self, post_id: int):
        try:
            request = post_pb2.PostRequest(post_id=post_id)
            return self.stub.GetPost(request)
        except grpc.RpcError as e:
            log_msg(f"Error in get_post: {str(e)}")
            raise

    def update_post(self, post_id: int, title: str = None, content: str = None,
                   visibility: str = None, property_type: str = None,
                   location: str = None, map_location: str = None,
                   price: float = None, status: str = None):
        try:
            request = post_pb2.PostUpdateRequest(
                post_id=post_id,
                title=title,
                content=content,
                visibility=visibility,
                property_type=property_type,
                location=location,
                map_location=map_location,
                price=price,
                status=status
            )
            return self.stub.UpdatePost(request)
        except grpc.RpcError as e:
            log_msg(f"Error in update_post: {str(e)}")
            raise

    def delete_post(self, post_id: int):
        try:
            request = post_pb2.PostRequest(post_id=post_id)
            return self.stub.DeletePost(request)
        except grpc.RpcError as e:
            log_msg(f"Error in delete_post: {str(e)}")
            raise

    def get_posts_by_user(self, user_id: int, page: int = 1, limit: int = 10):
        try:
            request = post_pb2.GetPostsByUserRequest(
                user_id=user_id,
                page=page,
                limit=limit
            )
            return self.stub.GetPostsByUser(request)
        except grpc.RpcError as e:
            log_msg(f"Error in get_posts_by_user: {str(e)}")
            raise

    def search_posts(self, property_type: str = None, location: str = None,
                    min_price: float = None, max_price: float = None,
                    status: str = None, page: int = 1, limit: int = 10):
        try:
            request = post_pb2.SearchPostsRequest(
                property_type=property_type,
                location=location,
                min_price=min_price or 0.0,
                max_price=max_price or 0.0,
                status=status,
                page=page,
                limit=limit
            )
            return self.stub.SearchPosts(request)
        except grpc.RpcError as e:
            log_msg(f"Error in search_posts: {str(e)}")
            raise

    def add_post_media(self, post_id: int, media):
        try:
            request = post_pb2.PostMediaRequest(
                post_id=post_id,
                media=media
            )
            return self.stub.AddPostMedia(request)
        except grpc.RpcError as e:
            log_msg(f"Error in add_post_media: {str(e)}")
            raise

    def delete_post_media(self, media_id: int):
        try:
            request = post_pb2.PostRequest(post_id=media_id)
            return self.stub.DeletePostMedia(request)
        except grpc.RpcError as e:
            log_msg(f"Error in delete_post_media: {str(e)}")
            raise

    def like_post(self, post_id: int, user_id: int, reaction_type: str = 'like'):
        try:
            request = post_pb2.LikeRequest(
                id=post_id,
                user_id=user_id,
                reaction_type=reaction_type
            )
            return self.stub.LikePost(request)
        except grpc.RpcError as e:
            log_msg(f"Error in like_post: {str(e)}")
            raise

    def unlike_post(self, post_id: int, user_id: int):
        try:
            request = post_pb2.LikeRequest(
                id=post_id,
                user_id=user_id
            )
            return self.stub.UnlikePost(request)
        except grpc.RpcError as e:
            log_msg(f"Error in unlike_post: {str(e)}")
            raise

    def create_comment(self, post_id: int, user_id: int, comment: str, parent_comment_id: int = None):
        try:
            request = post_pb2.CommentCreateRequest(
                post_id=post_id,
                user_id=user_id,
                comment=comment,
                parent_comment_id=parent_comment_id or 0
            )
            return self.stub.CreateComment(request)
        except grpc.RpcError as e:
            log_msg(f"Error in create_comment: {str(e)}")
            raise

    def update_comment(self, comment_id: int, comment: str = None, status: str = None):
        try:
            request = post_pb2.CommentUpdateRequest(
                comment_id=comment_id,
                comment=comment,
                status=status
            )
            return self.stub.UpdateComment(request)
        except grpc.RpcError as e:
            log_msg(f"Error in update_comment: {str(e)}")
            raise

    def delete_comment(self, comment_id: int):
        try:
            request = post_pb2.PostRequest(post_id=comment_id)
            return self.stub.DeleteComment(request)
        except grpc.RpcError as e:
            log_msg(f"Error in delete_comment: {str(e)}")
            raise

    def get_comments(self, post_id: int, page: int = 1, limit: int = 10):
        try:
            request = post_pb2.GetCommentsRequest(
                post_id=post_id,
                page=page,
                limit=limit
            )
            return self.stub.GetComments(request)
        except grpc.RpcError as e:
            log_msg(f"Error in get_comments: {str(e)}")
            raise

    def like_comment(self, comment_id: int, user_id: int, reaction_type: str = 'like'):
        try:
            request = post_pb2.LikeRequest(
                id=comment_id,
                user_id=user_id,
                reaction_type=reaction_type
            )
            return self.stub.LikeComment(request)
        except grpc.RpcError as e:
            log_msg(f"Error in like_comment: {str(e)}")
            raise

    def unlike_comment(self, comment_id: int, user_id: int):
        try:
            request = post_pb2.LikeRequest(
                id=comment_id,
                user_id=user_id
            )
            return self.stub.UnlikeComment(request)
        except grpc.RpcError as e:
            log_msg(f"Error in unlike_comment: {str(e)}")
            raise

class PropertyServiceClient:
    def __init__(self, host='localhost', port=50053):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = property_pb2_grpc.PropertyServiceStub(self.channel)

    def create_property(self, **property_data):
        request = property_pb2.Property(**property_data)
        return self.stub.CreateProperty(request)

    def get_property(self, property_id: str):
        request = property_pb2.PropertyRequest(property_id=property_id)
        return self.stub.GetProperty(request)

    def update_property(self, property_id: str, **property_data):
        property_data['property_id'] = property_id
        request = property_pb2.Property(**property_data)
        return self.stub.UpdateProperty(request)

    def delete_property(self, property_id: str):
        request = property_pb2.PropertyRequest(property_id=property_id)
        return self.stub.DeleteProperty(request)

    def search_properties(self, **search_params):
        request = property_pb2.PropertySearchRequest(**search_params)
        return self.stub.SearchProperties(request)

    def list_properties(self):
        request = property_pb2.PropertyRequest()
        return self.stub.ListProperties(request)

    def increment_view_count(self, property_id: str):
        request = property_pb2.PropertyRequest(property_id=property_id)
        return self.stub.IncrementViewCount(request)

# Create singleton instances
auth_client = AuthServiceClient()
user_client = UserServiceClient()
comments_client = CommentsServiceClient()
posts_client = PostsServiceClient()
property_client = PropertyServiceClient()

import grpc
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from app.proto_files.user import user_pb2, user_pb2_grpc
import app.proto_files.comments.comments_pb2 as comments_pb2
import app.proto_files.comments.comments_pb2_grpc as comments_pb2_grpc
import app.proto_files.posts.post_pb2 as post_pb2
import app.proto_files.posts.post_pb2_grpc as post_pb2_grpc
from app.proto_files.property import property_pb2, property_pb2_grpc
from app.proto_files.auth import auth_pb2, auth_pb2_grpc

class AuthServiceClient:
    def __init__(self, host='localhost', port=50052):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)

    def login(self, email: str, password: str):
        request = auth_pb2.LoginRequest(
            email=email,
            password=password
        )
        return self.stub.Login(request)

    def send_otp(self, email: str):
        request = auth_pb2.OTPRequest(
            email=email
        )
        return self.stub.SendOTP(request)

    def verify_otp(self, email: str, otp_code: str):
        request = auth_pb2.VerifyOTPRequest(
            email=email,
            otp_code=otp_code
        )
        return self.stub.VerifyOTP(request)

    def forgot_password(self, email_or_phone: str):
        request = auth_pb2.ForgotPasswordRequest(
            email_or_phone=email_or_phone
        )
        return self.stub.ForgotPassword(request)

    def reset_password(self, email_or_phone: str, otp_code: str, new_password: str):
        request = auth_pb2.ResetPasswordRequest(
            email_or_phone=email_or_phone,
            otp_code=otp_code,
            new_password=new_password
        )
        return self.stub.ResetPassword(request)

class UserServiceClient:
    def __init__(self, host='localhost', port=50051):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = user_pb2_grpc.UserServiceStub(self.channel)

    def get_user(self, user_id):
        request = user_pb2.UserRequest(id=user_id)
        return self.stub.GetUser(request)

    def create_user(self, name, email, phone, password, role, location):
        request = user_pb2.CreateUserRequest(
            name=name,
            email=email,
            phone=phone,
            password=password,
            role=role,
            location=location
        )
        return self.stub.CreateUser(request)

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
    def __init__(self, host='localhost', port=50052):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = post_pb2_grpc.PostsServiceStub(self.channel)

    def create_post(self, user_id: str, title: str, content: str):
        request = post_pb2.PostCreateRequest(
            user_id=user_id,
            title=title,
            content=content
        )
        return self.stub.CreatePost(request)

    def get_post(self, post_id: str):
        request = post_pb2.PostRequest(post_id=post_id)
        return self.stub.GetPost(request)

    def update_post(self, post_id: str, title: str, content: str):
        request = post_pb2.PostUpdateRequest(
            post_id=post_id,
            title=title,
            content=content
        )
        return self.stub.UpdatePost(request)

    def delete_post(self, post_id: str):
        request = post_pb2.PostRequest(post_id=post_id)
        return self.stub.DeletePost(request)

    def get_posts_by_user(self, user_id: str):
        request = post_pb2.GetPostsByUserRequest(user_id=user_id)
        return self.stub.GetPostsByUser(request)

    def like_post(self, post_id: str, user_id: str):
        request = post_pb2.LikePostRequest(
            post_id=post_id,
            user_id=user_id
        )
        return self.stub.LikePost(request)

    def unlike_post(self, post_id: str, user_id: str):
        request = post_pb2.LikePostRequest(
            post_id=post_id,
            user_id=user_id
        )
        return self.stub.UnlikePost(request)

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

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

# Create singleton instances
user_client = UserServiceClient()
comments_client = CommentsServiceClient()

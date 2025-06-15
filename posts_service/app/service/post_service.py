import grpc
from concurrent import futures
import os
import sys
from sqlalchemy.orm import Session
from ..repository.post_repository import PostRepository
from ..entity.post_entity import Post
from typing import List, Optional
from datetime import datetime

# Add the app directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_dir)

from app.proto_files import post_pb2, post_pb2_grpc

class PostService:
    def __init__(self, db: Session):
        self.repository = PostRepository(db)

    def create_post(self, user_id: int, title: str, content: str) -> post_pb2.Post:
        post = post_pb2.Post(
            user_id=user_id,
            title=title,
            content=content,
            created_at=int(datetime.now().timestamp()),
            updated_at=int(datetime.now().timestamp()),
            like_count=0,
            comment_count=0
        )
        return self.repository.create_post(post)

    def get_post(self, post_id: int) -> Optional[post_pb2.Post]:
        return self.repository.get_post(post_id)

    def get_posts_by_user(self, user_id: int) -> List[post_pb2.Post]:
        return self.repository.get_posts_by_user(user_id)

    def update_post(self, post_id: int, title: str, content: str) -> Optional[post_pb2.Post]:
        return self.repository.update_post(post_id, title, content)

    def delete_post(self, post_id: int) -> bool:
        return self.repository.delete_post(post_id)

    def like_post(self, post_id: int, user_id: int) -> Optional[post_pb2.Post]:
        return self.repository.like_post(post_id, user_id)

    def unlike_post(self, post_id: int, user_id: int) -> Optional[post_pb2.Post]:
        return self.repository.unlike_post(post_id, user_id)

    def increment_comment_count(self, post_id: int) -> Optional[post_pb2.Post]:
        return self.repository.increment_comment_count(post_id)

    def decrement_comment_count(self, post_id: int) -> Optional[post_pb2.Post]:
        return self.repository.decrement_comment_count(post_id)

class PostsService(post_pb2_grpc.PostsServiceServicer):
    def CreatePost(self, request, context):
        try:
            # Create a new post
            post = post_pb2.Post(
                post_id="1",  # This should be generated
                user_id=request.user_id,
                title=request.title,
                content=request.content,
                created_at=int(datetime.now().timestamp()),
                updated_at=int(datetime.now().timestamp()),
                like_count=0,
                comment_count=0
            )
            return post_pb2.PostResponse(
                success=True,
                message="Post created successfully",
                post=post
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.PostResponse(
                success=False,
                message=f"Failed to create post: {str(e)}"
            )

    def GetPost(self, request, context):
        try:
            # Create a sample post with the correct field names
            post = post_pb2.Post(
                post_id=request.post_id,
                user_id="sample_user",  # This should come from database
                title="Sample Post",
                content="Sample Content",
                created_at=int(datetime.now().timestamp()),
                updated_at=int(datetime.now().timestamp()),
                like_count=0,
                comment_count=0
            )
            return post_pb2.PostResponse(
                success=True,
                message="Post retrieved successfully",
                post=post
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.PostResponse(
                success=False,
                message=f"Failed to get post: {str(e)}"
            )

    def UpdatePost(self, request, context):
        try:
            post = post_pb2.Post(
                post_id=request.post_id,
                user_id="sample_user",  # This should come from database
                title=request.title,
                content=request.content,
                created_at=int(datetime.now().timestamp()),
                updated_at=int(datetime.now().timestamp()),
                like_count=0,
                comment_count=0
            )
            return post_pb2.PostResponse(
                success=True,
                message="Post updated successfully",
                post=post
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.PostResponse(
                success=False,
                message=f"Failed to update post: {str(e)}"
            )

    def DeletePost(self, request, context):
        try:
            # Implement actual deletion logic here
            return post_pb2.PostResponse(
                success=True,
                message="Post deleted successfully"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.PostResponse(
                success=False,
                message=f"Failed to delete post: {str(e)}"
            )

    def GetPostsByUser(self, request, context):
        try:
            # Create sample posts for the user
            posts = [
                post_pb2.Post(
                    post_id="1",
                    user_id=request.user_id,  # Using user_id from the request
                    title="Sample Post 1",
                    content="Sample Content 1",
                    created_at=int(datetime.now().timestamp()),
                    updated_at=int(datetime.now().timestamp()),
                    like_count=0,
                    comment_count=0
                ),
                post_pb2.Post(
                    post_id="2",
                    user_id=request.user_id,  # Using user_id from the request
                    title="Sample Post 2",
                    content="Sample Content 2",
                    created_at=int(datetime.now().timestamp()),
                    updated_at=int(datetime.now().timestamp()),
                    like_count=0,
                    comment_count=0
                )
            ]
            post_list = post_pb2.PostList(posts=posts)
            return post_pb2.PostListResponse(
                success=True,
                message="Posts retrieved successfully",
                posts=post_list
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.PostListResponse(
                success=False,
                message=f"Failed to get posts: {str(e)}"
            )

    def LikePost(self, request, context):
        try:
            post = post_pb2.Post(
                post_id=request.post_id,
                user_id=request.user_id,
                title="Sample Post",
                content="Sample Content",
                created_at=int(datetime.now().timestamp()),
                updated_at=int(datetime.now().timestamp()),
                like_count=1,  # Incremented
                comment_count=0
            )
            return post_pb2.PostResponse(
                success=True,
                message="Post liked successfully",
                post=post
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.PostResponse(
                success=False,
                message=f"Failed to like post: {str(e)}"
            )

    def UnlikePost(self, request, context):
        try:
            post = post_pb2.Post(
                post_id=request.post_id,
                user_id=request.user_id,
                title="Sample Post",
                content="Sample Content",
                created_at=int(datetime.now().timestamp()),
                updated_at=int(datetime.now().timestamp()),
                like_count=0,  # Decremented
                comment_count=0
            )
            return post_pb2.PostResponse(
                success=True,
                message="Post unliked successfully",
                post=post
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.PostResponse(
                success=False,
                message=f"Failed to unlike post: {str(e)}"
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    post_pb2_grpc.add_PostsServiceServicer_to_server(PostsService(), server)
    server.add_insecure_port('[::]:50052')
    print("Starting posts service on port 50052...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve() 
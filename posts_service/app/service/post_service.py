import grpc
from concurrent import futures
import os
import sys
from sqlalchemy.orm import Session
from ..repository.post_repository import PostRepository, SessionLocal
from ..entity.post_entity import Post
from typing import List, Optional
from datetime import datetime

# Add the app directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_dir)

from app.proto_files import post_pb2, post_pb2_grpc

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PostsService(post_pb2_grpc.PostsServiceServicer):
    def __init__(self):
        self.db = next(get_db())
        self.repository = PostRepository(self.db)

    def CreatePost(self, request, context):
        try:
            # Create a new post using repository
            post = self.repository.create_post(
                user_id=request.user_id,
                title=request.title,
                content=request.content
            )
            
            # Convert to proto message
            post_proto = post_pb2.Post(
                post_id=str(post.id),
                user_id=post.user_id,
                title=post.title,
                content=post.content,
                created_at=int(post.created_at.timestamp()),
                updated_at=int(post.updated_at.timestamp()),
                like_count=post.like_count,
                comment_count=post.comment_count
            )
            
            return post_pb2.PostResponse(
                success=True,
                message="Post created successfully",
                post=post_proto
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
            post = self.repository.get_post(int(request.post_id))
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return post_pb2.PostResponse(
                    success=False,
                    message="Post not found"
                )
            
            post_proto = post_pb2.Post(
                post_id=str(post.id),
                user_id=post.user_id,
                title=post.title,
                content=post.content,
                created_at=int(post.created_at.timestamp()),
                updated_at=int(post.updated_at.timestamp()),
                like_count=post.like_count,
                comment_count=post.comment_count
            )
            
            return post_pb2.PostResponse(
                success=True,
                message="Post retrieved successfully",
                post=post_proto
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
            post = self.repository.update_post(
                post_id=int(request.post_id),
                title=request.title,
                content=request.content
            )
            
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return post_pb2.PostResponse(
                    success=False,
                    message="Post not found"
                )
            
            post_proto = post_pb2.Post(
                post_id=str(post.id),
                user_id=post.user_id,
                title=post.title,
                content=post.content,
                created_at=int(post.created_at.timestamp()),
                updated_at=int(post.updated_at.timestamp()),
                like_count=post.like_count,
                comment_count=post.comment_count
            )
            
            return post_pb2.PostResponse(
                success=True,
                message="Post updated successfully",
                post=post_proto
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
            success = self.repository.delete_post(int(request.post_id))
            if not success:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return post_pb2.PostResponse(
                    success=False,
                    message="Post not found"
                )
            
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
            posts = self.repository.get_posts_by_user(request.user_id)
            
            post_protos = []
            for post in posts:
                post_proto = post_pb2.Post(
                    post_id=str(post.id),
                    user_id=post.user_id,
                    title=post.title,
                    content=post.content,
                    created_at=int(post.created_at.timestamp()),
                    updated_at=int(post.updated_at.timestamp()),
                    like_count=post.like_count,
                    comment_count=post.comment_count
                )
                post_protos.append(post_proto)
            
            post_list = post_pb2.PostList(posts=post_protos)
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
            post = self.repository.like_post(
                post_id=int(request.post_id),
                user_id=request.user_id
            )
            
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return post_pb2.PostResponse(
                    success=False,
                    message="Post not found"
                )
            
            post_proto = post_pb2.Post(
                post_id=str(post.id),
                user_id=post.user_id,
                title=post.title,
                content=post.content,
                created_at=int(post.created_at.timestamp()),
                updated_at=int(post.updated_at.timestamp()),
                like_count=post.like_count,
                comment_count=post.comment_count
            )
            
            return post_pb2.PostResponse(
                success=True,
                message="Post liked successfully",
                post=post_proto
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
            post = self.repository.unlike_post(
                post_id=int(request.post_id),
                user_id=request.user_id
            )
            
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return post_pb2.PostResponse(
                    success=False,
                    message="Post not found"
                )
            
            post_proto = post_pb2.Post(
                post_id=str(post.id),
                user_id=post.user_id,
                title=post.title,
                content=post.content,
                created_at=int(post.created_at.timestamp()),
                updated_at=int(post.updated_at.timestamp()),
                like_count=post.like_count,
                comment_count=post.comment_count
            )
            
            return post_pb2.PostResponse(
                success=True,
                message="Post unliked successfully",
                post=post_proto
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
    server.add_insecure_port('localhost:50052')
    print("Starting posts service on port 50052...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve() 
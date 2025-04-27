import grpc
from concurrent import futures
import os
import sys

# Add the app directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_dir)

from proto_files.post_pb2 import Post
from proto_files import post_pb2, post_pb2_grpc
from datetime import datetime

class PostsService(post_pb2_grpc.PostsServiceServicer):
    def CreatePost(self, request, context):
        # TODO: Implement create post logic
        post = Post(
            id="1",
            title=request.title,
            content=request.content,
            author_id=request.author_id,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            tags=request.tags,
            status="active"
        )
        return post_pb2.CreatePostResponse(post=post)

    def GetPost(self, request, context):
        # TODO: Implement get post logic
        post = Post(
            id=request.post_id,
            title="Sample Post",
            content="Sample Content",
            author_id="1",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            tags=["sample"],
            status="active"
        )
        return post_pb2.GetPostResponse(post=post)

    def ListPosts(self, request, context):
        # TODO: Implement list posts logic
        posts = [
            Post(
                id="1",
                title="Sample Post 1",
                content="Sample Content 1",
                author_id=request.author_id,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                tags=request.tags,
                status="active"
            )
        ]
        return post_pb2.ListPostsResponse(posts=posts, total_count=1)

    def UpdatePost(self, request, context):
        # TODO: Implement update post logic
        post = Post(
            id=request.post_id,
            title=request.title,
            content=request.content,
            author_id="1",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            tags=request.tags,
            status=request.status
        )
        return post_pb2.UpdatePostResponse(post=post)

    def DeletePost(self, request, context):
        # TODO: Implement delete post logic
        return post_pb2.DeletePostResponse(success=True)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    post_pb2_grpc.add_PostsServiceServicer_to_server(PostsService(), server)
    server.add_insecure_port('[::]:50052')
    print("Starting posts service on port 50052...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve() 
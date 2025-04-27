import grpc
from gateway.app.proto_files.user import user_pb2, user_pb2_grpc
from gateway.app.proto_files.posts import post_pb2, post_pb2_grpc

class UserServiceClient:
    def __init__(self):
        self.channel = grpc.insecure_channel("localhost:50051")
        self.stub = user_pb2_grpc.UserServiceStub(self.channel)

    def get_user(self, user_id):
        request = user_pb2.UserRequest(id=user_id)
        return self.stub.GetUser(request)

    def create_user(self, name, email, phone, password):
        request = user_pb2.CreateUserRequest(name=name, email=email, phone=phone, password=password)
        return self.stub.CreateUser(request)

class PostsServiceClient:
    def __init__(self, host='localhost', port=50052):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = post_pb2_grpc.PostsServiceStub(self.channel)

    def create_post(self, title, content, author_id, tags=None):
        request = post_pb2.CreatePostRequest(
            title=title,
            content=content,
            author_id=author_id,
            tags=tags or []
        )
        return self.stub.CreatePost(request)

    def get_post(self, post_id):
        request = post_pb2.GetPostRequest(post_id=post_id)
        return self.stub.GetPost(request)

    def list_posts(self, page=1, page_size=10, author_id=None, tags=None):
        request = post_pb2.ListPostsRequest(
            page=page,
            page_size=page_size,
            author_id=author_id or "",
            tags=tags or []
        )
        return self.stub.ListPosts(request)

    def update_post(self, post_id, title=None, content=None, tags=None, status=None):
        request = post_pb2.UpdatePostRequest(
            post_id=post_id,
            title=title or "",
            content=content or "",
            tags=tags or [],
            status=status or ""
        )
        return self.stub.UpdatePost(request)

    def delete_post(self, post_id):
        request = post_pb2.DeletePostRequest(post_id=post_id)
        return self.stub.DeletePost(request)

    def close(self):
        self.channel.close()

# Create singleton instances
user_client = UserServiceClient()
posts_client = PostsServiceClient()

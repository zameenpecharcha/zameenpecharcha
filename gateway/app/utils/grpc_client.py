import grpc
from gateway.app.proto_files.user import user_pb2, user_pb2_grpc
from gateway.app.proto_files.feed import feed_pb2, feed_pb2_grpc
from gateway.app.proto_files.comments import comments_pb2, comments_pb2_grpc
from gateway.app.proto_files.search import search_pb2, search_pb2_grpc
from gateway.app.proto_files.trending import trending_pb2, trending_pb2_grpc
from gateway.app.proto_files.property import property_pb2, property_pb2_grpc

class UserServiceClient:
    def __init__(self, host='localhost', port=50051):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = user_pb2_grpc.UserServiceStub(self.channel)

    def get_user(self, user_id):
        request = user_pb2.UserRequest(id=user_id)
        return self.stub.GetUser(request)

    def create_user(self, name, email, phone, password):
        request = user_pb2.CreateUserRequest(name=name, email=email, phone=phone, password=password)
        return self.stub.CreateUser(request)

class FeedServiceClient:
    def __init__(self, host='localhost', port=50052):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = feed_pb2_grpc.FeedServiceStub(self.channel)

    def create_post(self, user_id, content, latitude, longitude, location_name):
        request = feed_pb2.CreatePostRequest(
            user_id=user_id,
            content=content,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name
        )
        return self.stub.CreatePost(request)

    def get_post(self, post_id):
        request = feed_pb2.GetPostRequest(post_id=post_id)
        return self.stub.GetPost(request)

    def get_user_posts(self, user_id):
        request = feed_pb2.GetUserPostsRequest(user_id=user_id)
        return self.stub.GetUserPosts(request)

    def get_nearby_posts(self, latitude, longitude, radius_km=10.0):
        request = feed_pb2.GetNearbyPostsRequest(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )
        return self.stub.GetNearbyPosts(request)

    def update_post(self, post_id, content, latitude=None, longitude=None, location_name=None):
        request = feed_pb2.UpdatePostRequest(
            post_id=post_id,
            content=content,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name
        )
        return self.stub.UpdatePost(request)

    def delete_post(self, post_id):
        request = feed_pb2.DeletePostRequest(post_id=post_id)
        return self.stub.DeletePost(request)

    def like_post(self, post_id, user_id):
        request = feed_pb2.LikePostRequest(post_id=post_id, user_id=user_id)
        return self.stub.LikePost(request)

    def unlike_post(self, post_id, user_id):
        request = feed_pb2.UnlikePostRequest(post_id=post_id, user_id=user_id)
        return self.stub.UnlikePost(request)

class CommentsServiceClient:
    def __init__(self, host='localhost', port=50053):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = comments_pb2_grpc.CommentsServiceStub(self.channel)

    def create_comment(self, post_id, user_id, content):
        request = comments_pb2.CreateCommentRequest(
            post_id=post_id,
            user_id=user_id,
            content=content
        )
        return self.stub.CreateComment(request)

    def get_comment(self, comment_id):
        request = comments_pb2.GetCommentRequest(comment_id=comment_id)
        return self.stub.GetComment(request)

    def get_post_comments(self, post_id, page=1, page_size=10):
        request = comments_pb2.GetPostCommentsRequest(
            post_id=post_id,
            page=page,
            page_size=page_size
        )
        return self.stub.GetPostComments(request)

    def update_comment(self, comment_id, content):
        request = comments_pb2.UpdateCommentRequest(
            comment_id=comment_id,
            content=content
        )
        return self.stub.UpdateComment(request)

    def delete_comment(self, comment_id):
        request = comments_pb2.DeleteCommentRequest(comment_id=comment_id)
        return self.stub.DeleteComment(request)

    def like_comment(self, comment_id, user_id):
        request = comments_pb2.LikeCommentRequest(comment_id=comment_id, user_id=user_id)
        return self.stub.LikeComment(request)

    def unlike_comment(self, comment_id, user_id):
        request = comments_pb2.UnlikeCommentRequest(comment_id=comment_id, user_id=user_id)
        return self.stub.UnlikeComment(request)

class SearchServiceClient:
    def __init__(self, host='localhost', port=50054):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = search_pb2_grpc.SearchServiceStub(self.channel)

    def search_posts(self, query, page=1, page_size=10, latitude=None, longitude=None, radius_km=None):
        request = search_pb2.SearchPostsRequest(
            query=query,
            page=page,
            page_size=page_size,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )
        return self.stub.SearchPosts(request)

    def search_users(self, query, page=1, page_size=10):
        request = search_pb2.SearchUsersRequest(
            query=query,
            page=page,
            page_size=page_size
        )
        return self.stub.SearchUsers(request)

    def search_properties(self, query, page=1, page_size=10, min_price=None, max_price=None,
                         property_type=None, latitude=None, longitude=None, radius_km=None):
        request = search_pb2.SearchPropertiesRequest(
            query=query,
            page=page,
            page_size=page_size,
            min_price=min_price,
            max_price=max_price,
            property_type=property_type,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )
        return self.stub.SearchProperties(request)

class TrendingServiceClient:
    def __init__(self, host='localhost', port=50055):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = trending_pb2_grpc.TrendingServiceStub(self.channel)

    def get_trending_posts(self, limit=10, latitude=None, longitude=None, radius_km=None):
        request = trending_pb2.GetTrendingPostsRequest(
            limit=limit,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )
        return self.stub.GetTrendingPosts(request)

    def get_trending_properties(self, limit=10, property_type=None, min_price=None, max_price=None,
                              latitude=None, longitude=None, radius_km=None):
        request = trending_pb2.GetTrendingPropertiesRequest(
            limit=limit,
            property_type=property_type,
            min_price=min_price,
            max_price=max_price,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )
        return self.stub.GetTrendingProperties(request)

    def get_trending_locations(self, limit=10, latitude=None, longitude=None, radius_km=None):
        request = trending_pb2.GetTrendingLocationsRequest(
            limit=limit,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )
        return self.stub.GetTrendingLocations(request)

class PropertyServiceClient:
    def __init__(self, host='localhost', port=50056):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = property_pb2_grpc.PropertyServiceStub(self.channel)

    def create_property(self, user_id, title, description, price, property_type,
                       latitude, longitude, location_name, images=None, amenities=None):
        request = property_pb2.CreatePropertyRequest(
            user_id=user_id,
            title=title,
            description=description,
            price=price,
            property_type=property_type,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            images=images or [],
            amenities=amenities or []
        )
        return self.stub.CreateProperty(request)

    def get_property(self, property_id):
        request = property_pb2.GetPropertyRequest(property_id=property_id)
        return self.stub.GetProperty(request)

    def get_user_properties(self, user_id, page=1, page_size=10):
        request = property_pb2.GetUserPropertiesRequest(
            user_id=user_id,
            page=page,
            page_size=page_size
        )
        return self.stub.GetUserProperties(request)

    def update_property(self, property_id, title=None, description=None, price=None,
                       property_type=None, latitude=None, longitude=None, location_name=None,
                       images=None, amenities=None):
        request = property_pb2.UpdatePropertyRequest(
            property_id=property_id,
            title=title,
            description=description,
            price=price,
            property_type=property_type,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            images=images or [],
            amenities=amenities or []
        )
        return self.stub.UpdateProperty(request)

    def delete_property(self, property_id):
        request = property_pb2.DeletePropertyRequest(property_id=property_id)
        return self.stub.DeleteProperty(request)

    def get_nearby_properties(self, latitude, longitude, radius_km=10.0,
                            property_type=None, min_price=None, max_price=None):
        request = property_pb2.GetNearbyPropertiesRequest(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            property_type=property_type,
            min_price=min_price,
            max_price=max_price
        )
        return self.stub.GetNearbyProperties(request)

# Create singleton instances
user_client = UserServiceClient()
feed_client = FeedServiceClient()
comments_client = CommentsServiceClient()
search_client = SearchServiceClient()
trending_client = TrendingServiceClient()
property_client = PropertyServiceClient()

from app.clients.grpc_base_client import GRPCBaseClient
from app.proto_files.user import user_pb2, user_pb2_grpc


class UserServiceClient(GRPCBaseClient):
    def __init__(self):
        super().__init__(user_pb2_grpc.UserServiceStub, target='localhost:50051')

    def get_user(self, user_id: str,token=None):
        request = user_pb2.UserRequest(id=user_id)
        return self._call(self.stub.GetUser, request,token=token)

    def create_user(self, first_name, last_name, email, phone, password, role=None,
                   address=None, latitude=None, longitude=None, bio=None,token=None):
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
        return self._call(self.stub.CreateUser, request,token=token)

    def create_user_rating(self, rated_user_id, rated_by_user_id, rating_value, title=None, review=None, rating_type=None, is_anonymous=False, token=None):
        request = user_pb2.CreateRatingRequest(
            rated_user_id=rated_user_id,
            rated_by_user_id=rated_by_user_id,
            rating_value=rating_value,
            title=title or "",
            review=review,
            rating_type=rating_type,
            is_anonymous=is_anonymous
        )
        return self._call(self.stub.CreateRating, request,token=token)

    def get_user_ratings(self, user_id,token=None):
        request = user_pb2.UserRequest(id=user_id)
        return self._call(self.stub.GetUserRatings, request,token=token)

    def follow_user(self, user_id, following_id, followee_type: str = "", status: str = "active", token=None):
        request = user_pb2.FollowUserRequest(
            follower_id=user_id,
            following_id=following_id,
            followee_type=followee_type,
            status=status
        )
        return self._call(self.stub.FollowUser, request,token=token)

    def update_profile_photo(
        self,
        user_id: int,
        base64_data: str,
        file_name: str = None,
        content_type: str = None,
        caption: str = None,
        media_order: int = 1,
        token=None,
    ):
        request = user_pb2.UpdateUserPhotoRequest(
            user_id=user_id,
            media=user_pb2.MediaRequest(
                context_id=user_id,
                context_type="user_profile",
                media_type="image",
                base64_data=base64_data,
                file_name=file_name or "",
                content_type=content_type or "",
                media_order=media_order,
                caption=caption or "",
            ),
        )
        return self._call(self.stub.UpdateProfilePhoto, request, token=token)

    def update_cover_photo(
        self,
        user_id: int,
        base64_data: str,
        file_name: str = None,
        content_type: str = None,
        caption: str = None,
        media_order: int = 1,
        token=None,
    ):
        request = user_pb2.UpdateUserPhotoRequest(
            user_id=user_id,
            media=user_pb2.MediaRequest(
                context_id=user_id,
                context_type="user_cover",
                media_type="image",
                base64_data=base64_data,
                file_name=file_name or "",
                content_type=content_type or "",
                media_order=media_order,
                caption=caption or "",
            ),
        )
        return self._call(self.stub.UpdateCoverPhoto, request, token=token)

    def get_user_followers(self, user_id,token=None):
        request = user_pb2.UserRequest(id=user_id)
        return self._call(self.stub.GetUserFollowers, request,token=token)

    def get_user_following(self, user_id,token=None):
        request = user_pb2.UserRequest(id=user_id)
        return self._call(self.stub.GetUserFollowing, request,token=token)

    def check_following_status(self, user_id, following_id,token=None):
        request = user_pb2.CheckFollowingRequest(
            user_id=user_id,
            following_id=following_id
        )
        return self._call(self.stub.CheckFollowingStatus, request,token=token)


user_service_client = UserServiceClient()
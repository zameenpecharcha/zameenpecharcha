from app.proto_files.property import property_pb2_grpc, property_pb2
from app.clients.grpc_base_client import GRPCBaseClient


class PropertyServiceClient(GRPCBaseClient):
    def __init__(self):
        super().__init__(property_pb2_grpc.PropertyServiceStub, target='localhost:50054')

    # Basic property operations
    def create_property(self, **kwargs):
        request = property_pb2.Property(
            property_id=kwargs.get('property_id', ''),
            user_id=str(kwargs['user_id']),
            title=kwargs['title'],
            description=kwargs['description'],
            price=kwargs['price'],
            location=kwargs['location'],
            property_type=kwargs['property_type'],
            status=kwargs['status'],
            bedrooms=kwargs['bedrooms'],
            bathrooms=kwargs['bathrooms'],
            area=kwargs['area'],
            year_built=kwargs['year_built'],
            images=kwargs.get('images', []),
            amenities=kwargs.get('amenities', []),
            latitude=kwargs['latitude'],
            longitude=kwargs['longitude'],
            address=kwargs['address'],
            city=kwargs['city'],
            state=kwargs['state'],
            country=kwargs['country'],
            zip_code=kwargs['zip_code'],
            is_active=kwargs.get('is_active', True),
        )
        return self._call(self.stub.CreateProperty, request)

    def get_property(self, property_id: str):
        request = property_pb2.PropertyRequest(property_id=str(property_id))
        return self._call(self.stub.GetProperty, request)

    def update_property(self, **kwargs):
        # Same message as create; provide updated values
        request = property_pb2.Property(
            property_id=str(kwargs['property_id']),
            user_id=str(kwargs.get('user_id', '')),
            title=kwargs.get('title', ''),
            description=kwargs.get('description', ''),
            price=kwargs.get('price', 0.0),
            location=kwargs.get('location', ''),
            property_type=kwargs.get('property_type', 0),
            status=kwargs.get('status', 0),
            bedrooms=kwargs.get('bedrooms', 0),
            bathrooms=kwargs.get('bathrooms', 0),
            area=kwargs.get('area', 0.0),
            year_built=kwargs.get('year_built', 0),
            images=kwargs.get('images', []),
            amenities=kwargs.get('amenities', []),
            latitude=kwargs.get('latitude', 0.0),
            longitude=kwargs.get('longitude', 0.0),
            address=kwargs.get('address', ''),
            city=kwargs.get('city', ''),
            state=kwargs.get('state', ''),
            country=kwargs.get('country', ''),
            zip_code=kwargs.get('zip_code', ''),
            is_active=kwargs.get('is_active', True),
        )
        return self._call(self.stub.UpdateProperty, request)

    def delete_property(self, property_id: str):
        request = property_pb2.PropertyRequest(property_id=str(property_id))
        return self._call(self.stub.DeleteProperty, request)

    def search_properties(self, **kwargs):
        request = property_pb2.PropertySearchRequest(
            query=kwargs.get('query', ''),
            property_type=kwargs.get('property_type', 0),
            min_price=kwargs.get('min_price', 0.0),
            max_price=kwargs.get('max_price', 0.0),
            location=kwargs.get('location', ''),
            min_bedrooms=kwargs.get('min_bedrooms', 0),
            min_bathrooms=kwargs.get('min_bathrooms', 0),
            min_area=kwargs.get('min_area', 0.0),
            max_area=kwargs.get('max_area', 0.0),
        )
        return self._call(self.stub.SearchProperties, request)

    def list_properties(self, user_id: str = ''):
        request = property_pb2.PropertyRequest(property_id=str(user_id))
        return self._call(self.stub.ListProperties, request)

    def increment_view_count(self, property_id: str):
        request = property_pb2.PropertyRequest(property_id=str(property_id))
        return self._call(self.stub.IncrementViewCount, request)

    # Ratings
    def create_property_rating(self, property_id: int, rated_by_user_id: int, rating_value: int,
                               title: str = '', review: str = '', rating_type: str = '', is_anonymous: bool = False):
        request = property_pb2.PropertyRatingCreateRequest(
            property_id=property_id,
            rated_by_user_id=rated_by_user_id,
            rating_value=rating_value,
            title=title,
            review=review,
            rating_type=rating_type,
            is_anonymous=is_anonymous,
        )
        return self._call(self.stub.CreatePropertyRating, request)

    def get_property_ratings(self, property_id: int):
        request = property_pb2.PropertyRequest(property_id=str(property_id))
        return self._call(self.stub.GetPropertyRatings, request)

    # Followers
    def follow_property(self, user_id: int, property_id: int, status: str = 'active'):
        request = property_pb2.PropertyFollowRequest(
            user_id=user_id,
            property_id=property_id,
            status=status,
        )
        return self._call(self.stub.FollowProperty, request)

    def get_property_followers(self, property_id: int):
        request = property_pb2.PropertyRequest(property_id=str(property_id))
        return self._call(self.stub.GetPropertyFollowers, request)

    def add_property_media(self, property_id: int, media: list):
        uploads = []
        for m in media:
            uploads.append(property_pb2.PropertyMediaUpload(
                file_path=m.get('filePath') or m.get('file_path'),
                media_type=m.get('mediaType') or m.get('media_type') or 'image',
                media_order=m.get('mediaOrder') or m.get('media_order') or 1,
                caption=m.get('caption') or '',
                content_type=m.get('contentType') or m.get('content_type') or '',
            ))
        request = property_pb2.PropertyMediaRequest(property_id=property_id, media=uploads)
        return self._call(self.stub.AddPropertyMedia, request)


property_service_client = PropertyServiceClient()
import grpc
from concurrent import futures
import json
from ..proto_files import property_pb2, property_pb2_grpc
from ..repository.property_repository import (
    get_property_by_id, create_property, update_property,
    delete_property, get_user_properties, search_properties,
    get_properties, proto_to_db_property_type, proto_to_db_property_status,
    increment_view_count,
    create_property_rating, get_property_ratings,
    follow_property, get_property_followers,
)
import uuid

class PropertyService(property_pb2_grpc.PropertyServiceServicer):
    def GetProperty(self, request, context):
        try:
            property = get_property_by_id(request.property_id)
            if not property:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Property not found")
                return property_pb2.PropertyResponse(success=False, message="Property not found")

            # Parse JSON strings back to lists
            images = json.loads(property.images) if property.images else []
            amenities = json.loads(property.amenities) if property.amenities else []

            # Create Property message
            property_message = property_pb2.Property(
                property_id=str(property.property_id),
                user_id=str(property.user_id),
                title=property.title,
                description=property.description,
                price=property.price,
                location=property.location,
                property_type=property.property_type,
                status=property.status,
                images=images,
                bedrooms=property.bedrooms,
                bathrooms=property.bathrooms,
                area=property.area,
                year_built=property.year_built,
                amenities=amenities,
                latitude=property.latitude,
                longitude=property.longitude,
                address=property.address,
                city=property.city,
                state=property.state,
                country=property.country,
                zip_code=property.zip_code,
                is_active=property.is_active
            )

            return property_pb2.PropertyResponse(
                success=True,
                message="Property retrieved successfully",
                property=property_message
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyResponse(success=False, message=str(e))

    def CreateProperty(self, request, context):
        try:
            # Generate a new UUID for the property
            property_data = {
                'property_id': str(uuid.uuid4()),  # Generate new UUID
                'user_id': request.user_id,
                'title': request.title,
                'description': request.description,
                'price': request.price,
                'location': request.location,
                'property_type': request.property_type,
                'status': request.status,
                'bedrooms': request.bedrooms,
                'bathrooms': request.bathrooms,
                'area': request.area,
                'year_built': request.year_built,
                'images': request.images,
                'amenities': request.amenities,
                'latitude': request.latitude,
                'longitude': request.longitude,
                'address': request.address,
                'city': request.city,
                'state': request.state,
                'country': request.country,
                'zip_code': request.zip_code,
                'is_active': request.is_active
            }
            
            # Create property in database
            property_id = create_property(property_data)
            
            # Return the created property
            return self.GetProperty(property_pb2.PropertyRequest(property_id=property_id), context)
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Exception calling application: {str(e)}")
            return property_pb2.PropertyResponse(success=False, message=str(e))

    def UpdateProperty(self, request, context):
        try:
            property_data = {
                'user_id': request.user_id,
                'title': request.title,
                'description': request.description,
                'price': request.price,
                'location': request.location,
                'property_type': request.property_type,
                'status': request.status,
                'images': request.images,
                'bedrooms': request.bedrooms,
                'bathrooms': request.bathrooms,
                'area': request.area,
                'year_built': request.year_built,
                'amenities': request.amenities,
                'latitude': request.latitude,
                'longitude': request.longitude,
                'address': request.address,
                'city': request.city,
                'state': request.state,
                'country': request.country,
                'zip_code': request.zip_code,
                'is_active': request.is_active
            }
            
            success = update_property(request.property_id, property_data)
            if not success:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Property not found")
                return property_pb2.PropertyResponse(success=False, message="Property not found")
                
            return self.GetProperty(property_pb2.PropertyRequest(property_id=request.property_id), context)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Exception calling application: {str(e)}")
            return property_pb2.PropertyResponse(success=False, message=str(e))

    def DeleteProperty(self, request, context):
        try:
            success = delete_property(request.property_id)
            if not success:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Property not found")
                return property_pb2.PropertyResponse(success=False, message="Property not found")
            
            return property_pb2.PropertyResponse(
                success=True,
                message="Property deleted successfully"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Exception calling application: {str(e)}")
            return property_pb2.PropertyResponse(success=False, message=str(e))

    def GetUserProperties(self, request, context):
        properties = get_user_properties(request.user_id)
        return property_pb2.PropertiesResponse(
            properties=[self.GetProperty(property_pb2.PropertyRequest(property_id=p.property_id), context) for p in properties]
        )

    def SearchProperties(self, request, context):
        try:
            # Convert property type to database enum string
            property_type = None
            if hasattr(request, 'property_type'):
                property_type = proto_to_db_property_type.get(request.property_type, None)

            # Call repository with search parameters
            properties_list = search_properties(
                query=request.query,
                property_type=property_type,
                min_price=request.min_price if request.min_price > 0 else None,
                max_price=request.max_price if request.max_price > 0 else None,
                location=request.location if request.location else None,
                min_bedrooms=request.min_bedrooms if request.min_bedrooms > 0 else None,
                min_bathrooms=request.min_bathrooms if request.min_bathrooms > 0 else None,
                min_area=request.min_area if request.min_area > 0 else None,
                max_area=request.max_area if request.max_area > 0 else None,
                skip=0,  # Default values for pagination
                limit=10
            )

            # Convert properties to response format
            property_list = property_pb2.PropertyList()
            for prop in properties_list:
                # Parse JSON strings back to lists
                images = json.loads(prop.images) if prop.images else []
                amenities = json.loads(prop.amenities) if prop.amenities else []

                property_message = property_pb2.Property(
                    property_id=str(prop.property_id),
                    user_id=str(prop.user_id),
                    title=prop.title,
                    description=prop.description,
                    price=prop.price,
                    location=prop.location,
                    property_type=prop.property_type,
                    status=prop.status,
                    images=images,
                    bedrooms=prop.bedrooms,
                    bathrooms=prop.bathrooms,
                    area=prop.area,
                    year_built=prop.year_built,
                    amenities=amenities,
                    latitude=prop.latitude,
                    longitude=prop.longitude,
                    address=prop.address,
                    city=prop.city,
                    state=prop.state,
                    country=prop.country,
                    zip_code=prop.zip_code,
                    is_active=prop.is_active
                )
                property_list.properties.append(property_message)

            return property_pb2.PropertyListResponse(
                success=True,
                message="Properties found successfully",
                properties=property_list
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Exception calling application: {str(e)}")
            return property_pb2.PropertyListResponse(success=False, message=str(e))

    def ListProperties(self, request, context):
        try:
            # Get properties with default pagination
            properties_list = get_properties(skip=0, limit=10)

            # Convert properties to response format
            property_list = property_pb2.PropertyList()
            for prop in properties_list:
                # Parse JSON strings back to lists
                images = json.loads(prop.images) if prop.images else []
                amenities = json.loads(prop.amenities) if prop.amenities else []

                property_message = property_pb2.Property(
                    property_id=str(prop.property_id),
                    user_id=str(prop.user_id),
                    title=prop.title,
                    description=prop.description,
                    price=prop.price,
                    location=prop.location,
                    property_type=prop.property_type,
                    status=prop.status,
                    images=images,
                    bedrooms=prop.bedrooms,
                    bathrooms=prop.bathrooms,
                    area=prop.area,
                    year_built=prop.year_built,
                    amenities=amenities,
                    latitude=prop.latitude,
                    longitude=prop.longitude,
                    address=prop.address,
                    city=prop.city,
                    state=prop.state,
                    country=prop.country,
                    zip_code=prop.zip_code,
                    is_active=prop.is_active
                )
                property_list.properties.append(property_message)

            return property_pb2.PropertyListResponse(
                success=True,
                message="Properties retrieved successfully",
                properties=property_list
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Exception calling application: {str(e)}")
            return property_pb2.PropertyListResponse(success=False, message=str(e))

    def IncrementViewCount(self, request, context):
        try:
            success = increment_view_count(request.property_id)
            if not success:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Property not found")
                return property_pb2.PropertyResponse(success=False, message="Property not found")
            
            # Get updated property
            return self.GetProperty(property_pb2.PropertyRequest(property_id=request.property_id), context)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Exception calling application: {str(e)}")
            return property_pb2.PropertyResponse(success=False, message=str(e))

    # --- Ratings ---
    def CreatePropertyRating(self, request, context):
        try:
            if not 1 <= request.rating_value <= 5:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Rating value must be between 1 and 5")
                return property_pb2.PropertyRatingResponse()

            rating_id = create_property_rating(
                property_id=int(request.property_id),
                rated_by_user_id=int(request.rated_by_user_id),
                rating_value=request.rating_value,
                title=request.title,
                review=request.review,
                rating_type=request.rating_type,
                is_anonymous=request.is_anonymous,
            )
            # Fetch the created row
            rows = get_property_ratings(int(request.property_id))
            for r in rows:
                if r.id == rating_id:
                    return property_pb2.PropertyRatingResponse(
                        id=r.id,
                        property_id=r.rated_id,
                        rated_by_user_id=r.rated_by,
                        rating_value=r.rating_value,
                        title=r.title or "",
                        review=r.review or "",
                        rating_type=r.rating_type or "",
                        is_anonymous=bool(r.is_anonymous),
                        created_at=0,
                        updated_at=0,
                    )
            return property_pb2.PropertyRatingResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyRatingResponse()

    def GetPropertyRatings(self, request, context):
        try:
            rows = get_property_ratings(int(request.property_id))
            ratings = []
            for r in rows:
                ratings.append(property_pb2.PropertyRatingResponse(
                    id=r.id,
                    property_id=r.rated_id,
                    rated_by_user_id=r.rated_by,
                    rating_value=r.rating_value,
                    title=r.title or "",
                    review=r.review or "",
                    rating_type=r.rating_type or "",
                    is_anonymous=bool(r.is_anonymous),
                    created_at=0,
                    updated_at=0,
                ))
            return property_pb2.PropertyRatingsResponse(ratings=ratings)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyRatingsResponse()

    # --- Followers ---
    def FollowProperty(self, request, context):
        try:
            follow_id = follow_property(
                user_id=int(request.user_id),
                property_id=int(request.property_id),
                status=request.status or 'active',
            )
            # Return the created relation
            rows = get_property_followers(int(request.property_id))
            for f in rows:
                if f.id == follow_id:
                    return property_pb2.PropertyFollowResponse(
                        id=f.id,
                        user_id=f.follower_id,
                        property_id=f.following_id,
                        status=f.status or "",
                        followed_at=0,
                    )
            return property_pb2.PropertyFollowResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyFollowResponse()

    def GetPropertyFollowers(self, request, context):
        try:
            rows = get_property_followers(int(request.property_id))
            followers = []
            for f in rows:
                followers.append(property_pb2.PropertyFollowResponse(
                    id=f.id,
                    user_id=f.follower_id,
                    property_id=f.following_id,
                    status=f.status or "",
                    followed_at=0,
                ))
            return property_pb2.PropertyFollowersResponse(followers=followers)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyFollowersResponse()

from ..interceptors.auth_interceptor import AuthServerInterceptor


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[AuthServerInterceptor()],
    )
    property_pb2_grpc.add_PropertyServiceServicer_to_server(PropertyService(), server)
    server.add_insecure_port('localhost:50054')
    print("Starting property service on port 50054...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve() 
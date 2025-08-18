import grpc
from sqlalchemy import select
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
    add_property_media, update_property_media_url_size,
    get_property_media_urls,
)
import uuid

def _to_int(value, default=0):
    try:
        if value is None:
            return default
        if isinstance(value, int):
            return value
        if isinstance(value, (float,)):
            return int(value)
        v = str(value).strip()
        return int(v) if v.lstrip('-').isdigit() else default
    except Exception:
        return default

def _to_epoch(dt) -> int:
    try:
        if dt is None:
            return 0
        # If it's already a numeric value
        if isinstance(dt, (int, float)):
            return int(dt)
        # SQLAlchemy may return datetime
        from datetime import datetime
        if isinstance(dt, datetime):
            return int(dt.timestamp())
        # Fallback: try to parse string
        return int(float(str(dt)))
    except Exception:
        return 0

def _format_ts(dt) -> str:
    try:
        if dt is None:
            return ""
        from datetime import datetime
        if isinstance(dt, datetime):
            return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
        # If it's epoch seconds
        if isinstance(dt, (int, float)):
            return datetime.fromtimestamp(dt).strftime("%Y-%m-%d %H:%M:%S.%f")
        # Try parse from string epoch
        as_float = float(str(dt))
        return datetime.fromtimestamp(as_float).strftime("%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        return ""
def _map_property_type(val):
    # Map DB stored value (string or number) to proto enum int
    from ..proto_files import property_pb2
    if isinstance(val, int):
        return val
    s = str(val).upper() if val is not None else ''
    if s in ("0", "APARTMENT"): return property_pb2.APARTMENT
    if s in ("1", "VILLA"): return property_pb2.VILLA
    if s in ("2", "HOUSE"): return property_pb2.HOUSE
    if s in ("3", "LAND"): return property_pb2.LAND
    try:
        return int(s)
    except Exception:
        return property_pb2.APARTMENT

def _map_property_status(val):
    # Map DB stored value (string or number) to proto enum int
    from ..proto_files import property_pb2
    if isinstance(val, int):
        return val
    s = str(val).upper() if val is not None else ''
    if s in ("0", "ACTIVE"): return property_pb2.ACTIVE
    if s in ("1", "INACTIVE"): return property_pb2.INACTIVE
    if s in ("2", "SOLD"): return property_pb2.SOLD
    if s in ("3", "RENTED"): return property_pb2.RENTED
    try:
        return int(s)
    except Exception:
        return property_pb2.ACTIVE

class PropertyService(property_pb2_grpc.PropertyServiceServicer):
    def GetProperty(self, request, context):
        try:
            property = get_property_by_id(request.property_id)
            if not property:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Property not found")
                return property_pb2.PropertyResponse(success=False, message="Property not found")

            # Collections not stored as JSON per DDL; leave empty or derive when implemented
            images = []
            amenities = []

            # Create Property message
            image_urls = get_property_media_urls(property.id)
            property_message = property_pb2.Property(
                property_id=str(property.id),
                user_id="",
                title=property.title or "",
                description=property.description or "",
                price=float(property.price) if property.price is not None else 0.0,
                location=property.location or "",
                property_type=_map_property_type(property.property_type),
                status=_map_property_status(property.status),
                images=image_urls,
                bedrooms=_to_int(getattr(property, 'bedrooms', 0), 0),
                bathrooms=0,
                area=float(getattr(property, 'area_size', 0.0) or 0.0),
                year_built=_to_int(getattr(property, 'year_build', None), 0),
                amenities=amenities,
                latitude=float(property.latitude) if property.latitude is not None else 0.0,
                longitude=float(property.longitude) if property.longitude is not None else 0.0,
                address=getattr(property, 'address', "") or "",
                city=property.city or "",
                state=property.state or "",
                country=property.country or "",
                zip_code=getattr(property, 'pin_code', "") or "",
                is_active=True,
                cover_photo_id=_to_int(getattr(property, 'cover_photo_id', None), 0),
                profile_photo_id=_to_int(getattr(property, 'profile_photo_id', None), 0),
                created_at=_format_ts(getattr(property, 'created_at', None)),
                updated_at=_format_ts(getattr(property, 'updated_at', None)),
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
            property_data = {
                'user_id': request.user_id,
                'title': request.title,
                'description': request.description,
                'price': request.price,
                'location': request.location,
                'property_type': request.property_type,
                'status': request.status,
                'bedrooms': request.bedrooms,
                'area': request.area,
                'year_built': request.year_built,
                'latitude': request.latitude,
                'longitude': request.longitude,
                'city': request.city,
                'state': request.state,
                'country': request.country,
                'zip_code': request.zip_code,
                'is_active': request.is_active,
            }
            # Only set photo ids if provided with valid ids (>0)
            try:
                if getattr(request, 'cover_photo_id') and int(request.cover_photo_id) > 0:
                    property_data['cover_photo_id'] = int(request.cover_photo_id)
            except Exception:
                pass
            try:
                if getattr(request, 'profile_photo_id') and int(request.profile_photo_id) > 0:
                    property_data['profile_photo_id'] = int(request.profile_photo_id)
            except Exception:
                pass
            
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
                'bedrooms': request.bedrooms,
                'area': request.area,
                'year_built': request.year_built,
                'latitude': request.latitude,
                'longitude': request.longitude,
                'city': request.city,
                'state': request.state,
                'country': request.country,
                'zip_code': request.zip_code,
                'is_active': request.is_active,
            }
            try:
                if getattr(request, 'cover_photo_id') and int(request.cover_photo_id) > 0:
                    property_data['cover_photo_id'] = int(request.cover_photo_id)
            except Exception:
                pass
            try:
                if getattr(request, 'profile_photo_id') and int(request.profile_photo_id) > 0:
                    property_data['profile_photo_id'] = int(request.profile_photo_id)
            except Exception:
                pass
            
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
                images = []
                amenities = []

                property_message = property_pb2.Property(
                    property_id=str(prop.id),
                    user_id="",
                    title=prop.title or "",
                    description=prop.description or "",
                    price=float(prop.price) if prop.price is not None else 0.0,
                    location=prop.location or "",
                    property_type=_map_property_type(prop.property_type),
                    status=_map_property_status(prop.status),
                    images=images,
                    bedrooms=_to_int(getattr(prop, 'bedrooms', 0), 0),
                    bathrooms=0,
                    area=float(getattr(prop, 'area_size', 0.0) or 0.0),
                    year_built=_to_int(getattr(prop, 'year_build', None), 0),
                    amenities=amenities,
                    latitude=float(prop.latitude) if prop.latitude is not None else 0.0,
                    longitude=float(prop.longitude) if prop.longitude is not None else 0.0,
                    address=getattr(prop, 'address', "") or "",
                    city=prop.city or "",
                    state=prop.state or "",
                    country=prop.country or "",
                    zip_code=getattr(prop, 'pin_code', "") or "",
                    is_active=True,
                    created_at=_format_ts(getattr(prop, 'created_at', None)),
                    updated_at=_format_ts(getattr(prop, 'updated_at', None)),
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
                images = []
                amenities = []

                property_message = property_pb2.Property(
                    property_id=str(prop.id),
                    user_id="",
                    title=prop.title or "",
                    description=prop.description or "",
                    price=float(prop.price) if prop.price is not None else 0.0,
                    location=prop.location or "",
                    property_type=_map_property_type(prop.property_type),
                    status=_map_property_status(prop.status),
                    images=images,
                    bedrooms=_to_int(getattr(prop, 'bedrooms', 0), 0),
                    bathrooms=0,
                    area=float(getattr(prop, 'area_size', 0.0) or 0.0),
                    year_built=_to_int(getattr(prop, 'year_build', None), 0),
                    amenities=amenities,
                    latitude=float(prop.latitude) if prop.latitude is not None else 0.0,
                    longitude=float(prop.longitude) if prop.longitude is not None else 0.0,
                    address=getattr(prop, 'address', "") or "",
                    city=prop.city or "",
                    state=prop.state or "",
                    country=prop.country or "",
                    zip_code=getattr(prop, 'pin_code', "") or "",
                    is_active=True,
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
                        created_at=_format_ts(getattr(r, 'created_at', None)),
                        updated_at=_format_ts(getattr(r, 'updated_at', None)),
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
                    created_at=_format_ts(getattr(r, 'created_at', None)),
                    updated_at=_format_ts(getattr(r, 'updated_at', None)),
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
                # Always accept immediately for properties
                status='active',
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
                        followed_at=_format_ts(getattr(f, 'followed_at', None)),
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
                    followed_at=_format_ts(getattr(f, 'followed_at', None)),
                ))
            return property_pb2.PropertyFollowersResponse(followers=followers)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyFollowersResponse()

    def AddPropertyMedia(self, request, context):
        try:
            from ..utils.s3_utils import upload_file_to_s3, build_property_media_key
            uploaded_items = []
            for m in request.media:
                file_name = m.file_path.split('/')[-1]
                # Pre-insert to get media_id
                media_id = add_property_media(
                    property_id=int(request.property_id),
                    media_type=(m.media_type or 'image'),
                    media_order=(m.media_order or 1),
                    caption=(m.caption or None),
                )
                key = build_property_media_key(request.property_id, media_id, file_name)
                public_url, size_bytes = upload_file_to_s3(
                    file_path=m.file_path,
                    key=key,
                    content_type=(m.content_type or None),
                )
                update_property_media_url_size(media_id, public_url, size_bytes)

                uploaded_items.append(property_pb2.PropertyMediaItem(
                    id=media_id,
                    property_id=request.property_id,
                    media_type=(m.media_type or 'image'),
                    media_url=public_url,
                    media_order=(m.media_order or 1),
                    media_size=size_bytes,
                    caption=m.caption or "",
                    uploaded_at=_format_ts(None),
                ))

            return property_pb2.PropertyMediaResponse(success=True, message="Media uploaded", media=uploaded_items)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyMediaResponse(success=False, message=str(e))

    def UpdatePropertyProfilePhoto(self, request, context):
        try:
            import os
            from ..utils.s3_utils import upload_file_to_s3, build_property_media_key
            pid = int(request.property_id)
            m = request.media
            file_path = str(getattr(m, 'file_path', '') or '')
            if not file_path:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("file_path is required")
                return property_pb2.PropertyResponse(success=False, message="file_path is required")
            file_name = os.path.basename(file_path)
            # Pre-insert media for the property (context_type kept generic 'property')
            media_id = add_property_media(
                property_id=pid,
                media_type=(m.media_type or 'image'),
                media_order=int(m.media_order) if getattr(m, 'media_order', None) not in (None, 0) else 1,
                caption=(m.caption or None),
            )
            key = build_property_media_key(pid, media_id, file_name)
            public_url, size_bytes = upload_file_to_s3(
                file_path=file_path,
                key=key,
                content_type=(m.content_type or None),
            )
            update_property_media_url_size(media_id, public_url, size_bytes)

            # Update properties.profile_photo_id = media_id
            update_property(pid, { 'profile_photo_id': media_id })

            return self.GetProperty(property_pb2.PropertyRequest(property_id=str(pid)), context)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyResponse(success=False, message=str(e))

    def UpdatePropertyCoverPhoto(self, request, context):
        try:
            import os
            from ..utils.s3_utils import upload_file_to_s3, build_property_media_key
            pid = int(request.property_id)
            m = request.media
            file_path = str(getattr(m, 'file_path', '') or '')
            if not file_path:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("file_path is required")
                return property_pb2.PropertyResponse(success=False, message="file_path is required")
            file_name = os.path.basename(file_path)
            media_id = add_property_media(
                property_id=pid,
                media_type=(m.media_type or 'image'),
                media_order=int(m.media_order) if getattr(m, 'media_order', None) not in (None, 0) else 1,
                caption=(m.caption or None),
            )
            key = build_property_media_key(pid, media_id, file_name)
            public_url, size_bytes = upload_file_to_s3(
                file_path=file_path,
                key=key,
                content_type=(m.content_type or None),
            )
            update_property_media_url_size(media_id, public_url, size_bytes)

            # Update properties.cover_photo_id = media_id
            update_property(pid, { 'cover_photo_id': media_id })

            return self.GetProperty(property_pb2.PropertyRequest(property_id=str(pid)), context)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return property_pb2.PropertyResponse(success=False, message=str(e))

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
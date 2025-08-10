import typing
import strawberry
from enum import Enum
from app.exception.UserException import REException
from app.utils.log_utils import log_msg
from app.clients.property.property_client import property_service_client
from app.utils.auth import require_auth

@strawberry.enum
class PropertyType(Enum):
    APARTMENT = 0
    VILLA = 1
    HOUSE = 2
    LAND = 3

@strawberry.enum
class PropertyStatus(Enum):
    ACTIVE = 0
    INACTIVE = 1
    SOLD = 2
    RENTED = 3

@strawberry.type
class Property:
    propertyId: str = strawberry.field(name="propertyId")
    userId: str = strawberry.field(name="userId")
    title: str
    description: str
    price: float
    location: str
    propertyType: PropertyType = strawberry.field(name="propertyType")
    status: PropertyStatus
    bedrooms: int
    bathrooms: int
    area: float
    yearBuilt: int = strawberry.field(name="yearBuilt")
    images: typing.List[str]
    amenities: typing.List[str]
    createdAt: int = strawberry.field(name="createdAt")
    updatedAt: int = strawberry.field(name="updatedAt")
    viewCount: int = strawberry.field(name="viewCount")
    latitude: float
    longitude: float
    address: str
    city: str
    state: str
    country: str
    zipCode: str = strawberry.field(name="zipCode")
    isActive: bool = strawberry.field(name="isActive")

@strawberry.type
class Query:
    @strawberry.field
    def property(self, propertyId: str) -> typing.Optional[Property]:
        try:
            response = property_service_client.get_property(propertyId)
            if not response.success:
                raise REException("PROPERTY_NOT_FOUND", response.message, "Property not found")
            
            return Property(
                propertyId=response.property.property_id,
                userId=response.property.user_id,
                title=response.property.title,
                description=response.property.description,
                price=response.property.price,
                location=response.property.location,
                propertyType=response.property.property_type,
                status=response.property.status,
                bedrooms=response.property.bedrooms,
                bathrooms=response.property.bathrooms,
                area=response.property.area,
                yearBuilt=response.property.year_built,
                images=list(response.property.images),
                amenities=list(response.property.amenities),
                createdAt=response.property.created_at,
                updatedAt=response.property.updated_at,
                viewCount=response.property.view_count,
                latitude=response.property.latitude,
                longitude=response.property.longitude,
                address=response.property.address,
                city=response.property.city,
                state=response.property.state,
                country=response.property.country,
                zipCode=response.property.zip_code,
                isActive=response.property.is_active
            )
        except Exception as e:
            log_msg("error", f"Error fetching property: {str(e)}")
            raise REException(
                "PROPERTY_NOT_FOUND",
                "Failed to fetch property",
                str(e)
            ).to_graphql_error()

    @strawberry.field
    def search_properties(
        self,
        query: typing.Optional[str] = None,
        propertyType: typing.Optional[PropertyType] = None,
        minPrice: typing.Optional[float] = None,
        maxPrice: typing.Optional[float] = None,
        location: typing.Optional[str] = None,
        minBedrooms: typing.Optional[int] = None,
        minBathrooms: typing.Optional[int] = None,
        minArea: typing.Optional[float] = None,
        maxArea: typing.Optional[float] = None
    ) -> typing.List[Property]:
        try:
            response = property_service_client.search_properties(
                query=query or "",
                property_type=propertyType if propertyType is not None else 0,
                min_price=minPrice or 0,
                max_price=maxPrice or 0,
                location=location or "",
                min_bedrooms=minBedrooms or 0,
                min_bathrooms=minBathrooms or 0,
                min_area=minArea or 0,
                max_area=maxArea or 0
            )
            
            if not response.success:
                raise REException("PROPERTY_SEARCH_FAILED", response.message, "Failed to search properties")
            
            return [
                Property(
                    propertyId=prop.property_id,
                    userId=prop.user_id,
                    title=prop.title,
                    description=prop.description,
                    price=prop.price,
                    location=prop.location,
                    propertyType=prop.property_type,
                    status=prop.status,
                    bedrooms=prop.bedrooms,
                    bathrooms=prop.bathrooms,
                    area=prop.area,
                    yearBuilt=prop.year_built,
                    images=list(prop.images),
                    amenities=list(prop.amenities),
                    createdAt=prop.created_at,
                    updatedAt=prop.updated_at,
                    viewCount=prop.view_count,
                    latitude=prop.latitude,
                    longitude=prop.longitude,
                    address=prop.address,
                    city=prop.city,
                    state=prop.state,
                    country=prop.country,
                    zipCode=prop.zip_code,
                    isActive=prop.is_active
                )
                for prop in response.properties.properties
            ]
        except Exception as e:
            log_msg("error", f"Error searching properties: {str(e)}")
            raise REException(
                "PROPERTY_SEARCH_FAILED",
                "Failed to search properties",
                str(e)
            ).to_graphql_error()

    @strawberry.field
    def propertyRatings(self, propertyId: int) -> typing.List['PropertyRating']:
        try:
            response = property_service_client.get_property_ratings(propertyId)
            return [
                PropertyRating(
                    id=r.id,
                    propertyId=r.property_id,
                    ratedByUserId=r.rated_by_user_id,
                    ratingValue=r.rating_value,
                    title=r.title,
                    review=r.review,
                    ratingType=r.rating_type,
                    isAnonymous=r.is_anonymous,
                    createdAt=r.created_at,
                    updatedAt=r.updated_at,
                ) for r in response.ratings
            ]
        except Exception as e:
            log_msg("error", f"Error fetching property ratings: {str(e)}")
            raise REException(
                "PROPERTY_RATINGS_FAILED",
                "Failed to fetch ratings",
                str(e)
            ).to_graphql_error()

    @strawberry.field
    def propertyFollowers(self, propertyId: int) -> typing.List['PropertyFollow']:
        try:
            response = property_service_client.get_property_followers(propertyId)
            return [
                PropertyFollow(
                    id=f.id,
                    userId=f.user_id,
                    propertyId=f.property_id,
                    status=f.status,
                    followedAt=f.followed_at,
                ) for f in response.followers
            ]
        except Exception as e:
            log_msg("error", f"Error fetching property followers: {str(e)}")
            raise REException(
                "PROPERTY_FOLLOWERS_FAILED",
                "Failed to fetch followers",
                str(e)
            ).to_graphql_error()

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_property(
        self,
        userId: str,
        title: str,
        description: str,
        price: float,
        location: str,
        propertyType: PropertyType,
        status: PropertyStatus,
        bedrooms: int,
        bathrooms: int,
        area: float,
        yearBuilt: int,
        images: typing.List[str],
        amenities: typing.List[str],
        latitude: float,
        longitude: float,
        address: str,
        city: str,
        state: str,
        country: str,
        zipCode: str,
        isActive: bool = True
    ) -> Property:
        try:
            response = property_service_client.create_property(
                user_id=userId,
                title=title,
                description=description,
                price=price,
                location=location,
                property_type=propertyType.value,  # Convert enum to integer
                status=status.value,  # Convert enum to integer
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                area=area,
                year_built=yearBuilt,
                images=images,
                amenities=amenities,
                latitude=latitude,
                longitude=longitude,
                address=address,
                city=city,
                state=state,
                country=country,
                zip_code=zipCode,
                is_active=isActive
            )
            
            if not response.success:
                raise REException("PROPERTY_CREATION_FAILED", response.message, "Failed to create property")
            
            return Property(
                propertyId=response.property.property_id,
                userId=response.property.user_id,
                title=response.property.title,
                description=response.property.description,
                price=response.property.price,
                location=response.property.location,
                propertyType=PropertyType(response.property.property_type),  # Convert integer back to enum
                status=PropertyStatus(response.property.status),  # Convert integer back to enum
                bedrooms=response.property.bedrooms,
                bathrooms=response.property.bathrooms,
                area=response.property.area,
                yearBuilt=response.property.year_built,
                images=list(response.property.images),
                amenities=list(response.property.amenities),
                createdAt=response.property.created_at,
                updatedAt=response.property.updated_at,
                viewCount=response.property.view_count,
                latitude=response.property.latitude,
                longitude=response.property.longitude,
                address=response.property.address,
                city=response.property.city,
                state=response.property.state,
                country=response.property.country,
                zipCode=response.property.zip_code,
                isActive=response.property.is_active
            )
        except Exception as e:
            log_msg("error", f"Error creating property: {str(e)}")
            raise REException(
                "PROPERTY_CREATION_FAILED",
                "Failed to create property",
                str(e)
            ).to_graphql_error()

    @strawberry.mutation
    async def update_property(
        self,
        propertyId: str,
        title: typing.Optional[str] = None,
        description: typing.Optional[str] = None,
        price: typing.Optional[float] = None,
        location: typing.Optional[str] = None,
        propertyType: typing.Optional[PropertyType] = None,
        status: typing.Optional[PropertyStatus] = None,
        bedrooms: typing.Optional[int] = None,
        bathrooms: typing.Optional[int] = None,
        area: typing.Optional[float] = None,
        yearBuilt: typing.Optional[int] = None,
        images: typing.Optional[typing.List[str]] = None,
        amenities: typing.Optional[typing.List[str]] = None,
        latitude: typing.Optional[float] = None,
        longitude: typing.Optional[float] = None,
        address: typing.Optional[str] = None,
        city: typing.Optional[str] = None,
        state: typing.Optional[str] = None,
        country: typing.Optional[str] = None,
        zipCode: typing.Optional[str] = None,
        isActive: typing.Optional[bool] = None
    ) -> Property:
        try:
            # Get current property first
            current = property_service_client.get_property(propertyId)
            if not current.success:
                raise REException("PROPERTY_NOT_FOUND", current.message, "Property not found")
            
            # Update with new values or keep current ones
            response = property_service_client.update_property(
                property_id=propertyId,
                title=title or current.property.title,
                description=description or current.property.description,
                price=price or current.property.price,
                location=location or current.property.location,
                property_type=propertyType if propertyType is not None else current.property.property_type,
                status=status if status is not None else current.property.status,
                bedrooms=bedrooms or current.property.bedrooms,
                bathrooms=bathrooms or current.property.bathrooms,
                area=area or current.property.area,
                year_built=yearBuilt or current.property.year_built,
                images=images or list(current.property.images),
                amenities=amenities or list(current.property.amenities),
                latitude=latitude or current.property.latitude,
                longitude=longitude or current.property.longitude,
                address=address or current.property.address,
                city=city or current.property.city,
                state=state or current.property.state,
                country=country or current.property.country,
                zip_code=zipCode or current.property.zip_code,
                is_active=isActive if isActive is not None else current.property.is_active
            )
            
            if not response.success:
                raise REException("PROPERTY_UPDATE_FAILED", response.message, "Failed to update property")
            
            return Property(
                propertyId=response.property.property_id,
                userId=response.property.user_id,
                title=response.property.title,
                description=response.property.description,
                price=response.property.price,
                location=response.property.location,
                propertyType=response.property.property_type,
                status=response.property.status,
                bedrooms=response.property.bedrooms,
                bathrooms=response.property.bathrooms,
                area=response.property.area,
                yearBuilt=response.property.year_built,
                images=list(response.property.images),
                amenities=list(response.property.amenities),
                createdAt=response.property.created_at,
                updatedAt=response.property.updated_at,
                viewCount=response.property.view_count,
                latitude=response.property.latitude,
                longitude=response.property.longitude,
                address=response.property.address,
                city=response.property.city,
                state=response.property.state,
                country=response.property.country,
                zipCode=response.property.zip_code,
                isActive=response.property.is_active
            )
        except Exception as e:
            log_msg("error", f"Error updating property: {str(e)}")
            raise REException(
                "PROPERTY_UPDATE_FAILED",
                "Failed to update property",
                str(e)
            ).to_graphql_error()

    @strawberry.mutation
    async def delete_property(self, propertyId: str) -> bool:
        try:
            response = property_service_client.delete_property(propertyId)
            if not response.success:
                raise REException("PROPERTY_DELETION_FAILED", response.message, "Failed to delete property")
            return True
        except Exception as e:
            log_msg("error", f"Error deleting property: {str(e)}")
            raise REException(
                "PROPERTY_DELETION_FAILED",
                "Failed to delete property",
                str(e)
            ).to_graphql_error()

    @strawberry.mutation
    async def increment_view_count(self, propertyId: str) -> Property:
        try:
            response = property_service_client.increment_view_count(propertyId)
            if not response.success:
                raise REException("VIEW_COUNT_UPDATE_FAILED", response.message, "Failed to update view count")
            
            return Property(
                propertyId=response.property.property_id,
                userId=response.property.user_id,
                title=response.property.title,
                description=response.property.description,
                price=response.property.price,
                location=response.property.location,
                propertyType=response.property.property_type,
                status=response.property.status,
                bedrooms=response.property.bedrooms,
                bathrooms=response.property.bathrooms,
                area=response.property.area,
                yearBuilt=response.property.year_built,
                images=list(response.property.images),
                amenities=list(response.property.amenities),
                createdAt=response.property.created_at,
                updatedAt=response.property.updated_at,
                viewCount=response.property.view_count,
                latitude=response.property.latitude,
                longitude=response.property.longitude,
                address=response.property.address,
                city=response.property.city,
                state=response.property.state,
                country=response.property.country,
                zipCode=response.property.zip_code,
                isActive=response.property.is_active
            )
        except Exception as e:
            log_msg("error", f"Error incrementing view count: {str(e)}")
            raise REException(
                "VIEW_COUNT_UPDATE_FAILED",
                "Failed to increment view count",
                str(e)
            ).to_graphql_error() 

    @strawberry.mutation
    async def createPropertyRating(self, propertyId: int, ratedByUserId: int, ratingValue: int,
                                   title: typing.Optional[str] = "", review: typing.Optional[str] = "",
                                   ratingType: typing.Optional[str] = "", isAnonymous: typing.Optional[bool] = False) -> 'PropertyRating':
        try:
            response = property_service_client.create_property_rating(
                property_id=propertyId,
                rated_by_user_id=ratedByUserId,
                rating_value=ratingValue,
                title=title or "",
                review=review or "",
                rating_type=ratingType or "",
                is_anonymous=isAnonymous or False,
            )
            return PropertyRating(
                id=response.id,
                propertyId=response.property_id,
                ratedByUserId=response.rated_by_user_id,
                ratingValue=response.rating_value,
                title=response.title,
                review=response.review,
                ratingType=response.rating_type,
                isAnonymous=response.is_anonymous,
                createdAt=response.created_at,
                updatedAt=response.updated_at,
            )
        except Exception as e:
            log_msg("error", f"Error creating property rating: {str(e)}")
            raise REException(
                "CREATE_PROPERTY_RATING_FAILED",
                "Failed to create property rating",
                str(e)
            ).to_graphql_error()

    @strawberry.mutation
    async def followProperty(self, userId: int, propertyId: int, status: typing.Optional[str] = 'active') -> 'PropertyFollow':
        try:
            response = property_service_client.follow_property(
                user_id=userId,
                property_id=propertyId,
                status=status or 'active',
            )
            return PropertyFollow(
                id=response.id,
                userId=response.user_id,
                propertyId=response.property_id,
                status=response.status,
                followedAt=response.followed_at,
            )
        except Exception as e:
            log_msg("error", f"Error following property: {str(e)}")
            raise REException(
                "FOLLOW_PROPERTY_FAILED",
                "Failed to follow property",
                str(e)
            ).to_graphql_error()

    @strawberry.input
    class PropertyMediaInput:
        filePath: str
        mediaType: typing.Optional[str] = "image"
        mediaOrder: typing.Optional[int] = 1
        caption: typing.Optional[str] = ""
        contentType: typing.Optional[str] = None

    @strawberry.type
    class PropertyMedia:
        id: int
        propertyId: int
        mediaType: str
        mediaUrl: str
        mediaOrder: int
        mediaSize: int
        caption: str
        uploadedAt: int

    @strawberry.type
    class PropertyMediaResponse:
        success: bool
        message: str
        media: typing.List[PropertyMedia]

    @strawberry.mutation
    async def addPropertyMedia(self, propertyId: int, media: typing.List[PropertyMediaInput]) -> PropertyMediaResponse:
        try:
            resp = property_service_client.add_property_media(
                property_id=propertyId,
                media=[m.__dict__ for m in media],
            )
            return PropertyMediaResponse(
                success=resp.success,
                message=resp.message,
                media=[
                    PropertyMedia(
                        id=item.id,
                        propertyId=item.property_id,
                        mediaType=item.media_type,
                        mediaUrl=item.media_url,
                        mediaOrder=item.media_order,
                        mediaSize=item.media_size,
                        caption=item.caption,
                        uploadedAt=item.uploaded_at,
                    ) for item in resp.media
                ],
            )
        except Exception as e:
            log_msg("error", f"Error adding property media: {str(e)}")
            raise REException(
                "ADD_PROPERTY_MEDIA_FAILED",
                "Failed to add property media",
                str(e)
            ).to_graphql_error()

@strawberry.type
class PropertyRating:
    id: int
    propertyId: int
    ratedByUserId: int
    ratingValue: int
    title: str
    review: str
    ratingType: str
    isAnonymous: bool
    createdAt: int
    updatedAt: int

@strawberry.type
class PropertyFollow:
    id: int
    userId: int
    propertyId: int
    status: str
    followedAt: int
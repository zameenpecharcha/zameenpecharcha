from fastapi import APIRouter, HTTPException
from ..utils.grpc_client import property_client
from ..schema.property_schema import Mutation, Query
import strawberry
from strawberry.asgi import GraphQL

router = APIRouter()

schema = strawberry.Schema(Query, Mutation)
graphql_app = GraphQL(schema)

router.add_route("/graphql", graphql_app)

@router.post("/properties")
async def create_property(
    user_id: int,
    title: str,
    description: str,
    price: float,
    property_type: str,
    latitude: float,
    longitude: float,
    location_name: str,
    images: list = None,
    amenities: list = None
):
    try:
        response = property_client.create_property(
            user_id=user_id,
            title=title,
            description=description,
            price=price,
            property_type=property_type,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            images=images,
            amenities=amenities
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/properties/{property_id}")
async def get_property(property_id: int):
    try:
        response = property_client.get_property(property_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/properties")
async def get_user_properties(user_id: int, page: int = 1, page_size: int = 10):
    try:
        response = property_client.get_user_properties(user_id, page, page_size)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/properties/{property_id}")
async def update_property(
    property_id: int,
    title: str = None,
    description: str = None,
    price: float = None,
    property_type: str = None,
    latitude: float = None,
    longitude: float = None,
    location_name: str = None,
    images: list = None,
    amenities: list = None
):
    try:
        response = property_client.update_property(
            property_id=property_id,
            title=title,
            description=description,
            price=price,
            property_type=property_type,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            images=images,
            amenities=amenities
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/properties/{property_id}")
async def delete_property(property_id: int):
    try:
        response = property_client.delete_property(property_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/properties/nearby")
async def get_nearby_properties(
    latitude: float,
    longitude: float,
    radius_km: float = 10.0,
    property_type: str = None,
    min_price: float = None,
    max_price: float = None
):
    try:
        response = property_client.get_nearby_properties(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            property_type=property_type,
            min_price=min_price,
            max_price=max_price
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
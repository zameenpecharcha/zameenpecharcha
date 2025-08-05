from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PropertyDocument(BaseModel):
    id: Optional[int] = None
    property_id: int
    doc_name: Optional[str]
    doc_url: Optional[str]
    uploaded_by: Optional[int]
    is_verified: bool = False

class PropertyFeature(BaseModel):
    id: Optional[int] = None
    property_id: int
    feature_name: Optional[str]
    feature_value: Optional[str]

class Media(BaseModel):
    id: Optional[int] = None
    context_id: Optional[int]
    context_type: Optional[str]
    media_type: Optional[str]
    media_url: Optional[str]
    media_order: int = 0
    media_size: Optional[int]
    caption: Optional[str]
    uploaded_at: Optional[datetime]

class UserProperty(BaseModel):
    id: Optional[int] = None
    user_id: int
    property_id: int
    role: Optional[str]
    is_primary: bool = False
    added_at: Optional[datetime]

class Property(BaseModel):
    id: Optional[int] = None
    title: Optional[str]
    builder_name: Optional[str]
    project_name: Optional[str]
    rera_id: Optional[str]
    year_build: Optional[int]
    no_of_floors: Optional[int]
    no_of_units: Optional[int]
    building_amenities: Optional[str]
    verification_status: Optional[str]
    verified_by: Optional[int]
    like_count: int = 0
    is_flagged: bool = False
    average_rating: float = 0.0
    review_count: int = 0
    description: Optional[str]
    property_type: Optional[str]
    listing_type: Optional[str]
    price: Optional[float]
    area_size: Optional[float]
    bathroom_count: Optional[int]
    construction_status: Optional[str]
    availability_date: Optional[datetime]
    location: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    pin_code: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    status: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    documents: List[PropertyDocument] = []
    features: List[PropertyFeature] = []
    media: List[Media] = []
    user_properties: List[UserProperty] = []

    class Config:
        orm_mode = True 
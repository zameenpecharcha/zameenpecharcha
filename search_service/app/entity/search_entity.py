from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON, Index, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class PropertyIndex(Base):
    __tablename__ = "property_index"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, unique=True)  # Removed ForeignKey since we don't need the relationship
    property_type = Column(String(50), nullable=False)  # residential, commercial, land
    property_subtype = Column(String(50))  # apartment, house, villa, etc.
    price = Column(Float, nullable=False)
    area = Column(Float, nullable=False)  # in square feet/meters
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    location = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    amenities = Column(JSON)  # List of amenities
    property_status = Column(String(50), nullable=False)  # for_sale, for_rent, sold
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Create indexes for common search fields
    __table_args__ = (
        Index('idx_property_type', 'property_type'),
        Index('idx_location', 'location'),
        Index('idx_price', 'price'),
        Index('idx_area', 'area'),
        Index('idx_property_status', 'property_status'),
        Index('idx_city_state', 'city', 'state'),
    )

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    search_query = Column(JSON, nullable=False)  # Store search parameters
    results_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Create index for user's search history
    __table_args__ = (
        Index('idx_user_search_history', 'user_id', 'created_at'),
    ) 
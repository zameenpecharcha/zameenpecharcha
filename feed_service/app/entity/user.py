from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from ..utils.db_connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    latitude = Column(Float)  # User's current latitude
    longitude = Column(Float)  # User's current longitude
    last_location_update = Column(DateTime, default=func.now())  # Track when location was last updated
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 
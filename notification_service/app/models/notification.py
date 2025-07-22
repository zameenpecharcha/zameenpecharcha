from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    type = Column(String(50))  # like, comment, trending
    message = Column(Text)
    entity_id = Column(Integer)  # post_id or comment_id
    entity_type = Column(String(50))  # post or comment
    is_read = Column(Boolean, default=False)
    context = Column(Text)  # Additional context as JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class LocationSubscription(Base):
    __tablename__ = "location_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    radius_km = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 
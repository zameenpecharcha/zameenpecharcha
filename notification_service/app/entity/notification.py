from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    type = Column(String, nullable=False)  # post_like, post_comment, comment_like, comment_reply, trending_post
    message = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)  # ID of the post/comment that triggered the notification
    entity_type = Column(String, nullable=False)  # post or comment
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    context = Column(String, nullable=True)  # Additional context like comment text, etc.

class LocationSubscription(Base):
    __tablename__ = "location_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_km = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True) 
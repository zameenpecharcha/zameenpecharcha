from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from ..utils.db_connection import Base
import uuid

class FeedItem(Base):
    __tablename__ = 'feed_items'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 
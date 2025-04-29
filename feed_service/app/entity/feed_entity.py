from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..utils.db_connection import Base

class FeedItem(Base):
    __tablename__ = "feed_items"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    user_id = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    post = relationship("Post", back_populates="feed_items") 
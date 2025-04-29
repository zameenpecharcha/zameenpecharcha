from sqlalchemy import Column, Integer, Float, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..utils.db_connection import Base

class TrendingPost(Base):
    __tablename__ = "trending_posts"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'), unique=True)
    score = Column(Float, nullable=False)  # Calculated score based on likes and comments
    rank = Column(Integer, nullable=False)  # Current rank in trending
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    post = relationship("Post", back_populates="trending_info") 
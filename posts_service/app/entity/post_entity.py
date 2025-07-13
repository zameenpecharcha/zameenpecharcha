from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from ..utils.db_connection import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)  # Changed from post_id to id
    user_id = Column(String, nullable=False)  # Changed from Integer to String to accept UUID
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)

# Association table for post likes
post_likes = Table(
    'post_likes',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),  # Changed to reference id
    Column('user_id', String, primary_key=True),  # Changed from Integer to String to accept UUID
    Column('created_at', TIMESTAMP, default=datetime.utcnow)
) 
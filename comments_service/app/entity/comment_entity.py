from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..utils.db_connection import Base

# Association table for comment likes
comment_likes = Table(
    'comment_likes',
    Base.metadata,
    Column('comment_id', UUID(as_uuid=True), ForeignKey('comments.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = Column(String, nullable=False)
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id", ondelete='CASCADE'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    like_count = Column(Integer, default=0)

    # Relationships
    replies = relationship("Comment", backref="parent", remote_side=[id], cascade="all, delete-orphan")
    # Removing the User relationship since we don't have access to the User model in this microservice
    # We'll handle likes through the likes table directly 
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from ..utils.db_connection import Base

# Association table for comment likes
comment_likes = Table(
    'comment_likes',
    Base.metadata,
    Column('comment_id', Integer, ForeignKey('comments.id'), primary_key=True),
    Column('user_id', Integer, primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    parent_comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    like_count = Column(Integer, default=0)

    # Relationships
    replies = relationship("Comment", backref="parent", remote_side=[id])
    likes = relationship("User", secondary=comment_likes, backref="liked_comments") 
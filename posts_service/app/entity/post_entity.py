from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..utils.db_connection import Base

meta = MetaData()

posts = Table('posts', meta,
    Column('post_id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.user_id')),
    Column('title', String(100)),
    Column('content', String(1000)),
    Column('created_at', TIMESTAMP),
    Column('updated_at', TIMESTAMP),
)

# Association table for post likes
post_likes = Table(
    'post_likes',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.post_id'), primary_key=True),
    Column('user_id', Integer, primary_key=True),
    Column('created_at', TIMESTAMP, default=datetime.utcnow)
)

class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)

    # Relationships
    likes = relationship("User", secondary=post_likes, backref="liked_posts") 
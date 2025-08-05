from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, text, Boolean, Float, ForeignKey, BigInteger
from datetime import datetime

meta = MetaData()

# Users table
users = Table('users', meta,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('first_name', String(50)),
    Column('last_name', String(50)),
    Column('email', String(100), unique=True, nullable=False),
    Column('phone', String(20)),
    Column('profile_photo', String(255)),
    Column('role', String(50)),
    Column('address', String(255)),
    Column('latitude', Float),
    Column('longitude', Float),
    Column('bio', String(500)),
    Column('password', String(100), nullable=False),
    Column('isactive', Boolean, server_default=text('true')),
    Column('email_verified', Boolean, server_default=text('false')),
    Column('phone_verified', Boolean, server_default=text('false')),
    Column('last_login_at', TIMESTAMP),
    Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
)

# Ratings table (updated schema)
ratings = Table('ratings', meta,
    Column('id', BigInteger, primary_key=True),
    Column('rated_user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('rated_by_user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('rating_value', Integer, nullable=False),
    Column('title', String),
    Column('review', String),
    Column('rating_type', String),
    Column('is_anonymous', Boolean, default=False),
    Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP')),
    Column('updated_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
)

# Followers table (updated schema)
followers = Table('followers', meta,
    Column('id', BigInteger, primary_key=True),
    Column('follower_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('following_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('followee_type', String),
    Column('status', String),
    Column('followed_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
)
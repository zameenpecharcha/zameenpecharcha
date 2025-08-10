from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, text, Boolean, Float, ForeignKey, BigInteger, Text

meta = MetaData()

# Users table
users = Table('users', meta,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('first_name', String(255)),
    Column('last_name', String(255)),
    Column('email', String(255), unique=True, nullable=False),
    Column('phone', String(255)),
    Column('role', String(255)),
    Column('address', String(255)),
    Column('latitude', Float),
    Column('longitude', Float),
    Column('bio', Text),
    Column('password', String(255), nullable=False),
    Column('isactive', Boolean, server_default=text('true')),
    Column('email_verified', Boolean, server_default=text('false')),
    Column('phone_verified', Boolean, server_default=text('false')),
    Column('gst_no', String(255)),
    Column('cover_photo_id', BigInteger, ForeignKey('media.id')),
    Column('profile_photo_id', BigInteger, ForeignKey('media.id')),
    Column('last_login_at', TIMESTAMP),
    Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
)

# Media table (needs to be before ratings and followers due to FK constraints)
media = Table('media', meta,
    Column('id', BigInteger, primary_key=True, nullable=False),
    Column('context_id', BigInteger),  # Generic foreign key for different contexts
    Column('context_type', String(255)),  # Type of context (e.g., 'user_profile', 'user_cover', etc.)
    Column('media_type', String(255)),    # Type of media (e.g., 'image', 'video', etc.)
    Column('media_url', Text),
    Column('media_order', Integer),
    Column('media_size', BigInteger),
    Column('caption', Text),
    Column('uploaded_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
)

// Ratings table - polymorphic
ratings = Table('ratings', meta,
    Column('id', BigInteger, primary_key=True, nullable=False),
    Column('rated_id', BigInteger, nullable=False),
    Column('rated_type', String(20), nullable=False),  # 'user' or 'property'
    Column('rated_by', BigInteger, nullable=False),    # user id who rated
    Column('rating_value', Integer, nullable=False),
    Column('title', String(255)),
    Column('review', Text),
    Column('rating_type', String(255)),
    Column('is_anonymous', Boolean, server_default=text('false')),
    Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP')),
    Column('updated_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
)

# Followers table - polymorphic followee
followers = Table('followers', meta,
    Column('id', BigInteger, primary_key=True, nullable=False),
    Column('follower_id', BigInteger, nullable=False),   # user who follows
    Column('following_id', BigInteger, nullable=False),  # id of user/property
    Column('followee_type', String(20)),                 # 'user' or 'property'
    Column('status', String(255)),
    Column('followed_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
)
from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid

meta = MetaData()

users = Table('users', meta,
    Column('user_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('name', String(50), nullable=False),
    Column('email', String(50), nullable=False, unique=True, index=True),
    Column('phone', Integer, unique=True, index=True),
    Column('profile_photo', String(50)),
    Column('role', String(50), nullable=False),
    Column('location', String(50)),
    Column('created_at', TIMESTAMP, nullable=False),
    Column('updated_at', TIMESTAMP),
    Column('bio', String(50)),
    Column('password', String(255), nullable=False),  # Increased length for hashed passwords
    Column('is_active', Boolean, default=True),
    Column('is_deleted', Boolean, default=False),
    Column('deleted_at', TIMESTAMP),
    Column('created_by', UUID(as_uuid=True)),
    Column('updated_by', UUID(as_uuid=True))
)
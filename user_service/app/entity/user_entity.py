from sqlalchemy import MetaData, Table, Column, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

meta = MetaData()

users = Table('users', meta,
    Column('user_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('name', String(50), nullable=False),
    Column('email', String(100), unique=True, nullable=False),  # Increased length for email
    Column('phone', String(15)),  # Changed to String for phone numbers
    Column('profile_photo', String(255)),  # Increased length for URLs
    Column('role', String(50)),
    Column('location', String(100)),  # Increased length for location data
    Column('created_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP')),
    Column('bio', String(500)),  # Increased length for bios
    Column('password', String(100), nullable=False),  # Increased length for hashed passwords
)
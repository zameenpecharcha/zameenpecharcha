from sqlalchemy import MetaData, Table, Column, Integer, String, Float, TIMESTAMP, Boolean, Text, BigInteger, ForeignKey
from sqlalchemy.sql import func

meta = MetaData()

properties = Table('properties', meta,
    Column('id', BigInteger, primary_key=True, nullable=False),
    Column('title', String, nullable=True),
    Column('builder_name', String, nullable=True),
    Column('project_name', String, nullable=True),
    Column('rera_id', String, nullable=True),
    Column('year_build', Integer, nullable=True),
    Column('no_of_floors', Integer, nullable=True),
    Column('no_of_units', Integer, nullable=True),
    Column('building_amenities', Text, nullable=True),
    Column('verification_status', String, nullable=True),
    Column('verified_by', BigInteger, nullable=True),  # FK to users table
    Column('like_count', Integer, default=0),
    Column('is_flagged', Boolean, default=False),
    Column('average_rating', Float, default=0.0),
    Column('review_count', Integer, default=0),
    Column('description', String, nullable=True),
    Column('property_type', String, nullable=True),
    Column('listing_type', String, nullable=True),
    Column('price', Float, nullable=True),
    Column('area_size', Float, nullable=True),
    Column('bathroom_count', Integer, nullable=True),
    Column('construction_status', String, nullable=True),
    Column('availability_date', TIMESTAMP, nullable=True),
    Column('location', Text, nullable=True),
    Column('city', String, nullable=True),
    Column('state', String, nullable=True),
    Column('country', String, nullable=True),
    Column('pin_code', String, nullable=True),
    Column('latitude', Float, nullable=True),
    Column('longitude', Float, nullable=True),
    Column('status', String, nullable=True),
    Column('created_at', TIMESTAMP, server_default=func.now()),
    Column('updated_at', TIMESTAMP, onupdate=func.now())
)

property_documents = Table('property_documents', meta,
    Column('id', BigInteger, primary_key=True, nullable=False),
    Column('property_id', BigInteger, ForeignKey('properties.id'), nullable=False),
    Column('doc_name', String, nullable=True),
    Column('doc_url', Text, nullable=True),
    Column('uploaded_by', BigInteger, nullable=True),  # FK to users table
    Column('is_verified', Boolean, default=False)
)

property_features = Table('property_features', meta,
    Column('id', BigInteger, primary_key=True, nullable=False),
    Column('property_id', BigInteger, ForeignKey('properties.id'), nullable=False),
    Column('feature_name', String, nullable=True),
    Column('feature_value', String, nullable=True)
)

media = Table('media', meta,
    Column('id', BigInteger, primary_key=True, nullable=False),
    Column('context_id', BigInteger, nullable=True),  # FK to various tables
    Column('context_type', String, nullable=True),
    Column('media_type', String, nullable=True),
    Column('media_url', String, nullable=True),
    Column('media_order', Integer, default=0),
    Column('media_size', Integer, nullable=True),
    Column('caption', Text, nullable=True),
    Column('uploaded_at', TIMESTAMP, server_default=func.now())
)

user_property = Table('user_property', meta,
    Column('id', BigInteger, primary_key=True, nullable=False),
    Column('user_id', BigInteger, nullable=False),  # FK to users table
    Column('property_id', BigInteger, ForeignKey('properties.id'), nullable=False),
    Column('role', String, nullable=True),
    Column('is_primary', Boolean, default=False),
    Column('added_at', TIMESTAMP, server_default=func.now())
) 
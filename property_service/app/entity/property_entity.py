from sqlalchemy import MetaData, Table, Column, Integer, String, Float, TIMESTAMP, Boolean, Enum as SQLEnum, BigInteger
from sqlalchemy.sql import func
from ..models.property import PropertyType, PropertyStatus

meta = MetaData()

# Define the enum values explicitly
PROPERTY_TYPES = ['APARTMENT', 'VILLA', 'HOUSE', 'LAND']
PROPERTY_STATUSES = ['ACTIVE', 'INACTIVE', 'SOLD', 'RENTED']

properties = Table('properties', meta,
    Column('id', BigInteger, primary_key=True),
    Column('title', String, nullable=True),
    Column('builder_name', String, nullable=True),
    Column('project_name', String, nullable=True),
    Column('rera_id', String, nullable=True),
    Column('year_build', Integer, nullable=True),
    Column('no_of_floors', Integer, nullable=True),
    Column('no_of_units', Integer, nullable=True),
    Column('buildings_amenities', String, nullable=True),
    Column('verification_status', String, nullable=True),
    Column('verified_by', BigInteger, nullable=True),
    Column('flag_count', Integer, nullable=True),
    Column('is_flagged', Boolean, nullable=True),
    Column('average_rating', Float, nullable=True),
    Column('review_count', Integer, nullable=True),
    Column('description', String, nullable=True),
    Column('property_type', String, nullable=True),
    Column('listing_type', String, nullable=True),
    Column('price', Float, nullable=True),
    Column('area_size', Float, nullable=True),
    Column('bedrooms', String, nullable=True),
    Column('construction_status', String, nullable=True),
    Column('availability_date', TIMESTAMP, nullable=True),
    Column('location', String, nullable=True),
    Column('city', String, nullable=True),
    Column('state', String, nullable=True),
    Column('country', String, nullable=True),
    Column('pin_code', String, nullable=True),
    Column('latitude', Float, nullable=True),
    Column('longitude', Float, nullable=True),
    Column('cover_photo_id', BigInteger, nullable=True),
    Column('profile_photo_id', BigInteger, nullable=True),
    Column('status', String, nullable=True),
    Column('created_at', TIMESTAMP, server_default=func.now()),
    Column('updated_at', TIMESTAMP, nullable=True)
)
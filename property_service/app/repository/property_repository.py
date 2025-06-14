from ..entity.property_entity import properties
from sqlalchemy.orm import sessionmaker
from ..utils.db_connection import get_db_engine
import json
from ..models.property import PropertyType, PropertyStatus
import uuid

SessionLocal = sessionmaker(bind=get_db_engine())

# Map proto enum int to Python Enum value
proto_to_python_property_type = {
    0: PropertyType.APARTMENT,
    1: PropertyType.VILLA,
    2: PropertyType.HOUSE,
    3: PropertyType.LAND
}

# Map proto enum int to Python Enum value for status
proto_to_python_property_status = {
    0: PropertyStatus.AVAILABLE,  # ACTIVE in proto
    1: PropertyStatus.PENDING,    # INACTIVE in proto
    2: PropertyStatus.SOLD,       # SOLD in proto
    3: PropertyStatus.RENTED      # RENTED in proto
}

def get_property_by_id(property_id):
    session = SessionLocal()
    query = properties.select().where(properties.c.property_id == property_id)
    property = session.execute(query).fetchone()
    session.close()
    return property

def create_property(property_data):
    session = SessionLocal()
    # Convert RepeatedScalarContainer to list before JSON serialization
    property_data['images'] = json.dumps(list(property_data.get('images', [])))
    property_data['amenities'] = json.dumps(list(property_data.get('amenities', [])))
    # Map proto enum int to Python Enum value
    property_data['property_type'] = proto_to_python_property_type.get(property_data['property_type'], PropertyType.APARTMENT)
    # Map proto enum int to Python Enum value for status
    property_data['status'] = proto_to_python_property_status.get(property_data['status'], PropertyStatus.AVAILABLE)
    # Convert string UUID to UUID object
    property_data['user_id'] = uuid.UUID(property_data['user_id'])
    
    result = session.execute(
        properties.insert().returning(properties.c.property_id).values(**property_data)
    )
    property_id = result.fetchone()[0]
    session.commit()
    session.close()
    return property_id

def update_property(property_id, property_data):
    session = SessionLocal()
    # Convert lists to JSON strings
    if 'images' in property_data:
        property_data['images'] = json.dumps(property_data['images'])
    if 'amenities' in property_data:
        property_data['amenities'] = json.dumps(property_data['amenities'])
    
    result = session.execute(
        properties.update()
        .where(properties.c.property_id == property_id)
        .values(**property_data)
    )
    session.commit()
    session.close()
    return result.rowcount > 0

def delete_property(property_id):
    session = SessionLocal()
    result = session.execute(
        properties.delete().where(properties.c.property_id == property_id)
    )
    session.commit()
    session.close()
    return result.rowcount > 0

def get_user_properties(user_id):
    session = SessionLocal()
    query = properties.select().where(properties.c.user_id == user_id)
    user_properties = session.execute(query).fetchall()
    session.close()
    return user_properties

def search_properties(query, skip=0, limit=10):
    session = SessionLocal()
    search_query = f"%{query}%"
    query = properties.select().where(
        (properties.c.title.ilike(search_query)) |
        (properties.c.description.ilike(search_query)) |
        (properties.c.location.ilike(search_query)) |
        (properties.c.city.ilike(search_query))
    ).offset(skip).limit(limit)
    results = session.execute(query).fetchall()
    session.close()
    return results

def get_properties(skip=0, limit=10, property_type=None, status=None, 
                  min_price=None, max_price=None, city=None):
    session = SessionLocal()
    query = properties.select()
    
    if property_type:
        query = query.where(properties.c.property_type == property_type)
    if status:
        query = query.where(properties.c.status == status)
    if min_price:
        query = query.where(properties.c.price >= min_price)
    if max_price:
        query = query.where(properties.c.price <= max_price)
    if city:
        query = query.where(properties.c.city == city)
        
    query = query.offset(skip).limit(limit)
    results = session.execute(query).fetchall()
    session.close()
    return results 
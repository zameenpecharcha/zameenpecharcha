from ..entity.property_entity import properties
from ..entity.media_entity import media as media_table
from ..entity.social_entity import ratings as ratings_table, followers as followers_table
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from ..utils.db_connection import get_db_engine
import json
from ..models.property import PropertyType, PropertyStatus

SessionLocal = sessionmaker(bind=get_db_engine())

# Map proto enum int to database enum string for property type
proto_to_db_property_type = {
    0: 'APARTMENT',
    1: 'VILLA',
    2: 'HOUSE',
    3: 'LAND'
}

# Map proto enum int to database enum string for status
proto_to_db_property_status = {
    0: 'ACTIVE',
    1: 'INACTIVE',
    2: 'SOLD',
    3: 'RENTED'
}

def get_property_by_id(property_id):
    session = SessionLocal()
    try:
        query = properties.select().where(properties.c.id == int(property_id))
        property = session.execute(query).fetchone()
        return property
    except ValueError:
        return None
    finally:
        session.close()

def create_property(property_data):
    session = SessionLocal()
    try:
        # Map incoming keys to DB columns and cast types (per create_tables.sql schema)
        # property_type, status, listing_type etc. are VARCHAR in DDL; pass through as provided
        if 'area' in property_data:
            property_data['area_size'] = property_data.pop('area')
        if 'zip_code' in property_data:
            property_data['pin_code'] = property_data.pop('zip_code')
        if 'year_built' in property_data:
            property_data['year_build'] = property_data.pop('year_built')
        # Drop fields not present in DDL
        property_data.pop('user_id', None)
        property_data.pop('is_active', None)
        
        result = session.execute(
            properties.insert().returning(properties.c.id).values(**property_data)
        )
        property_id = result.fetchone()[0]
        session.commit()
        return str(property_id)
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def update_property(property_id, property_data):
    session = SessionLocal()
    try:
        # Convert lists to JSON strings
        if 'images' in property_data:
            property_data['images'] = json.dumps(list(property_data['images']))
        if 'amenities' in property_data:
            property_data['amenities'] = json.dumps(list(property_data['amenities']))
        
        # Map proto enum int to database enum string
        if 'property_type' in property_data:
            property_data['property_type'] = proto_to_db_property_type.get(property_data['property_type'], 'APARTMENT')
        if 'status' in property_data:
            property_data['status'] = proto_to_db_property_status.get(property_data['status'], 'ACTIVE')
        
        # Map key changes and cast
        if 'area' in property_data:
            property_data['area_size'] = property_data.pop('area')
        if 'zip_code' in property_data:
            property_data['pin_code'] = property_data.pop('zip_code')
        if 'year_built' in property_data:
            property_data['year_build'] = property_data.pop('year_built')
        # Drop fields not present in DDL
        property_data.pop('user_id', None)
        property_data.pop('is_active', None)
        
        result = session.execute(
            properties.update()
            .where(properties.c.id == int(property_id))
            .values(**property_data)
        )
        session.commit()
        return result.rowcount > 0
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_property(property_id):
    session = SessionLocal()
    try:
        result = session.execute(
            properties.delete().where(properties.c.id == int(property_id))
        )
        session.commit()
        return result.rowcount > 0
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_user_properties(user_id):
    session = SessionLocal()
    query = properties.select().where(properties.c.user_id == int(user_id))
    user_properties = session.execute(query).fetchall()
    session.close()
    return user_properties

def create_property_rating(property_id: int, rated_by_user_id: int, rating_value: int, title: str = None, review: str = None, rating_type: str = None, is_anonymous: bool = False):
    session = SessionLocal()
    try:
        result = session.execute(
            ratings_table.insert().returning(ratings_table.c.id).values(
                rated_id=property_id,
                rated_type='property',
                rated_by=rated_by_user_id,
                rating_value=rating_value,
                title=title,
                review=review,
                rating_type=rating_type,
                is_anonymous=is_anonymous,
            )
        )
        session.commit()
        return result.scalar()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_property_ratings(property_id: int):
    session = SessionLocal()
    try:
        rows = session.execute(
            ratings_table.select().where(
                (ratings_table.c.rated_type == 'property') & (ratings_table.c.rated_id == property_id)
            )
        ).fetchall()
        return rows
    finally:
        session.close()

def follow_property(user_id: int, property_id: int, status: str = 'active'):
    session = SessionLocal()
    try:
        result = session.execute(
            followers_table.insert().returning(followers_table.c.id).values(
                follower_id=user_id,
                following_id=property_id,
                followee_type='property',
                status=status,
            )
        )
        session.commit()
        return result.scalar()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_property_followers(property_id: int):
    session = SessionLocal()
    try:
        rows = session.execute(
            followers_table.select().where(
                (followers_table.c.followee_type == 'property') & (followers_table.c.following_id == property_id)
            )
        ).fetchall()
        return rows
    finally:
        session.close()

def search_properties(query=None, property_type=None, min_price=None, max_price=None, 
                  location=None, min_bedrooms=None, min_bathrooms=None, 
                  min_area=None, max_area=None, skip=0, limit=10):
    session = SessionLocal()
    try:
        # Start with base query
        search_query = properties.select()

        # Add filters based on parameters
        if query:
            search_pattern = f"%{query}%"
            search_query = search_query.where(
                (properties.c.title.ilike(search_pattern)) |
                (properties.c.description.ilike(search_pattern)) |
                (properties.c.location.ilike(search_pattern)) |
                (properties.c.city.ilike(search_pattern))
            )

        if property_type is not None:
            search_query = search_query.where(properties.c.property_type == property_type)
        
        if min_price is not None:
            search_query = search_query.where(properties.c.price >= min_price)
        
        if max_price is not None:
            search_query = search_query.where(properties.c.price <= max_price)
        
        if location:
            location_pattern = f"%{location}%"
            search_query = search_query.where(properties.c.location.ilike(location_pattern))
        
        if min_bedrooms is not None:
            search_query = search_query.where(properties.c.bedrooms >= min_bedrooms)
        
        if min_bathrooms is not None:
            search_query = search_query.where(properties.c.bathrooms >= min_bathrooms)
        
        if min_area is not None:
            search_query = search_query.where(properties.c.area >= min_area)
        
        if max_area is not None:
            search_query = search_query.where(properties.c.area <= max_area)

        # Add pagination
        search_query = search_query.offset(skip).limit(limit)

        # Execute query
        results = session.execute(search_query).fetchall()
        return results
    except Exception as e:
        raise e
    finally:
        session.close()

def get_properties(skip=0, limit=10, property_type=None, status=None, 
                  min_price=None, max_price=None, city=None):
    session = SessionLocal()
    try:
        # Start with base query
        query = properties.select()
        
        # Add filters if provided
        if property_type:
            query = query.where(properties.c.property_type == property_type)
        if status:
            query = query.where(properties.c.status == status)
        if min_price is not None:
            query = query.where(properties.c.price >= min_price)
        if max_price is not None:
            query = query.where(properties.c.price <= max_price)
        if city:
            query = query.where(properties.c.city == city)
            
        # Add pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        results = session.execute(query).fetchall()
        return results
    except Exception as e:
        raise e
    finally:
        session.close()

def increment_view_count(property_id):
    session = SessionLocal()
    try:
        # Get current views and increment
        query = properties.select().where(properties.c.id == int(property_id))
        property = session.execute(query).fetchone()
        
        if not property:
            return False
            
        current_views = property.views or 0
        new_views = current_views + 1
        
        # Update views
        result = session.execute(
            properties.update()
            .where(properties.c.id == int(property_id))
            .values(views=new_views)
        )
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close() 

def create_property_media(property_id: int, media_type: str, media_url: str,
                          media_order: int = 1, media_size: int = 0, caption: str | None = None) -> int:
    session = SessionLocal()
    try:
        result = session.execute(
            media_table.insert().returning(media_table.c.id).values(
                context_id=property_id,
                context_type='property',
                media_type=media_type,
                media_url=media_url,
                media_order=media_order,
                media_size=media_size,
                caption=caption,
            )
        )
        session.commit()
        return result.scalar()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def add_property_media(property_id: int, media_type: str, media_order: int = 1, caption: str | None = None) -> int:
    session = SessionLocal()
    try:
        result = session.execute(
            media_table.insert().returning(media_table.c.id).values(
                context_id=property_id,
                context_type='property',
                media_type=media_type,
                media_url='',
                media_order=media_order,
                media_size=0,
                caption=caption,
            )
        )
        session.commit()
        return result.scalar()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def update_property_media_url_size(media_id: int, media_url: str, media_size: int) -> bool:
    session = SessionLocal()
    try:
        session.execute(
            media_table.update()
            .where(media_table.c.id == media_id)
            .values(media_url=media_url, media_size=media_size)
        )
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()

def get_property_media_urls(property_id: int):
    session = SessionLocal()
    try:
        rows = session.execute(
            select(media_table.c.media_url)
            .where(
                (media_table.c.context_id == int(property_id)) &
                (media_table.c.context_type == 'property')
            )
            .order_by(media_table.c.media_order)
        ).fetchall()
        return [r.media_url for r in rows if r.media_url]
    finally:
        session.close()
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from ..entity.property_entity import properties, property_documents, property_features, media, user_property
from ..utils.db_connection import get_db_session

class PropertyRepository:
    def __init__(self):
        self.session: Session = next(get_db_session())

    def get_property_by_id(self, property_id: int):
        """Get property by ID with all related data"""
        return self.session.query(properties)\
            .options(
                joinedload(properties.documents),
                joinedload(properties.features),
                joinedload(properties.media),
                joinedload(properties.user_properties)
            )\
            .filter(properties.c.id == property_id)\
            .first()

    def create_property(self, property_data: dict):
        """Create a new property"""
        result = self.session.execute(properties.insert().values(**property_data))
        self.session.commit()
        return self.get_property_by_id(result.inserted_primary_key[0])

    def update_property(self, property_id: int, property_data: dict):
        """Update an existing property"""
        self.session.execute(
            properties.update()
            .where(properties.c.id == property_id)
            .values(**property_data)
        )
        self.session.commit()
        return self.get_property_by_id(property_id)

    def delete_property(self, property_id: int) -> bool:
        """Delete a property and all related data"""
        try:
            # Delete related data first
            self.session.execute(property_documents.delete().where(property_documents.c.property_id == property_id))
            self.session.execute(property_features.delete().where(property_features.c.property_id == property_id))
            self.session.execute(media.delete().where(and_(media.c.context_id == property_id, media.c.context_type == 'property')))
            self.session.execute(user_property.delete().where(user_property.c.property_id == property_id))
            
            # Delete the property
            result = self.session.execute(properties.delete().where(properties.c.id == property_id))
            self.session.commit()
            return result.rowcount > 0
        except:
            self.session.rollback()
            raise

    def search_properties(self, **kwargs):
        """Search properties with filters and pagination"""
        query = self.session.query(properties)\
            .options(
                joinedload(properties.documents),
                joinedload(properties.features),
                joinedload(properties.media),
                joinedload(properties.user_properties)
            )

        # Apply filters
        if kwargs.get('query'):
            search_term = f"%{kwargs['query']}%"
            query = query.filter(
                or_(
                    properties.c.title.ilike(search_term),
                    properties.c.description.ilike(search_term),
                    properties.c.location.ilike(search_term),
                    properties.c.builder_name.ilike(search_term),
                    properties.c.project_name.ilike(search_term)
                )
            )

        if kwargs.get('property_type'):
            query = query.filter(properties.c.property_type == kwargs['property_type'])
        
        if kwargs.get('listing_type'):
            query = query.filter(properties.c.listing_type == kwargs['listing_type'])

        if kwargs.get('min_price'):
            query = query.filter(properties.c.price >= kwargs['min_price'])
        
        if kwargs.get('max_price'):
            query = query.filter(properties.c.price <= kwargs['max_price'])

        if kwargs.get('location'):
            query = query.filter(properties.c.location.ilike(f"%{kwargs['location']}%"))

        if kwargs.get('city'):
            query = query.filter(properties.c.city == kwargs['city'])

        if kwargs.get('state'):
            query = query.filter(properties.c.state == kwargs['state'])

        if kwargs.get('country'):
            query = query.filter(properties.c.country == kwargs['country'])

        if kwargs.get('min_bathrooms'):
            query = query.filter(properties.c.bathroom_count >= kwargs['min_bathrooms'])

        if kwargs.get('min_area'):
            query = query.filter(properties.c.area_size >= kwargs['min_area'])

        if kwargs.get('max_area'):
            query = query.filter(properties.c.area_size <= kwargs['max_area'])

        if kwargs.get('construction_status'):
            query = query.filter(properties.c.construction_status == kwargs['construction_status'])

        if kwargs.get('verification_status'):
            query = query.filter(properties.c.verification_status == kwargs['verification_status'])

        # Get total count
        total_count = query.count()

        # Apply pagination
        page = kwargs.get('page', 1)
        limit = kwargs.get('limit', 10)
        offset = (page - 1) * limit

        # Get paginated results
        properties_list = query.order_by(desc(properties.c.created_at))\
            .offset(offset)\
            .limit(limit)\
            .all()

        return properties_list, total_count

    def add_property_document(self, property_id: int, doc_name: str, doc_url: str, uploaded_by: int):
        """Add a document to a property"""
        result = self.session.execute(
            property_documents.insert().values(
                property_id=property_id,
                doc_name=doc_name,
                doc_url=doc_url,
                uploaded_by=uploaded_by
            )
        )
        self.session.commit()
        return result.inserted_primary_key[0]

    def add_property_feature(self, property_id: int, feature_name: str, feature_value: str):
        """Add a feature to a property"""
        result = self.session.execute(
            property_features.insert().values(
                property_id=property_id,
                feature_name=feature_name,
                feature_value=feature_value
            )
        )
        self.session.commit()
        return result.inserted_primary_key[0]

    def add_media(self, context_id: int, context_type: str, media_type: str, media_url: str, 
                 media_order: int = 0, media_size: int = 0, caption: str = None):
        """Add media to a property"""
        result = self.session.execute(
            media.insert().values(
                context_id=context_id,
                context_type=context_type,
                media_type=media_type,
                media_url=media_url,
                media_order=media_order,
                media_size=media_size,
                caption=caption
            )
        )
        self.session.commit()
        return result.inserted_primary_key[0]

    def add_user_property(self, user_id: int, property_id: int, role: str, is_primary: bool = False):
        """Add a user-property relationship"""
        result = self.session.execute(
            user_property.insert().values(
                user_id=user_id,
                property_id=property_id,
                role=role,
                is_primary=is_primary
            )
        )
        self.session.commit()
        return result.inserted_primary_key[0]

    def verify_property(self, property_id: int):
        """Mark a property as verified"""
        self.session.execute(
            properties.update()
            .where(properties.c.id == property_id)
            .values(verification_status='verified')
        )
        self.session.commit()
        return self.get_property_by_id(property_id)

    def flag_property(self, property_id: int):
        """Flag a property"""
        self.session.execute(
            properties.update()
            .where(properties.c.id == property_id)
            .values(is_flagged=True)
        )
        self.session.commit()
        return self.get_property_by_id(property_id) 
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..entity.search_entity import PropertyIndex, SearchHistory
from typing import List, Optional, Dict, Any
from datetime import datetime

class SearchRepository:
    def __init__(self, db: Session):
        self.db = db

    def index_property(self, property_data: Dict[str, Any]) -> Optional[PropertyIndex]:
        property_index = PropertyIndex(
            post_id=property_data['post_id'],
            property_type=property_data['property_type'],
            property_subtype=property_data.get('property_subtype'),
            price=property_data['price'],
            area=property_data['area'],
            bedrooms=property_data.get('bedrooms'),
            bathrooms=property_data.get('bathrooms'),
            location=property_data['location'],
            city=property_data['city'],
            state=property_data['state'],
            country=property_data['country'],
            latitude=property_data.get('latitude'),
            longitude=property_data.get('longitude'),
            amenities=property_data.get('amenities', []),
            property_status=property_data['property_status']
        )
        self.db.add(property_index)
        self.db.commit()
        self.db.refresh(property_index)
        return property_index

    def search_properties(self, filters: Dict[str, Any], limit: int = 20, offset: int = 0) -> List[PropertyIndex]:
        query = self.db.query(PropertyIndex)

        # Apply filters
        if filters.get('property_type'):
            query = query.filter(PropertyIndex.property_type == filters['property_type'])
        
        if filters.get('property_subtype'):
            query = query.filter(PropertyIndex.property_subtype == filters['property_subtype'])
        
        if filters.get('min_price'):
            query = query.filter(PropertyIndex.price >= filters['min_price'])
        
        if filters.get('max_price'):
            query = query.filter(PropertyIndex.price <= filters['max_price'])
        
        if filters.get('min_area'):
            query = query.filter(PropertyIndex.area >= filters['min_area'])
        
        if filters.get('max_area'):
            query = query.filter(PropertyIndex.area <= filters['max_area'])
        
        if filters.get('bedrooms'):
            query = query.filter(PropertyIndex.bedrooms == filters['bedrooms'])
        
        if filters.get('bathrooms'):
            query = query.filter(PropertyIndex.bathrooms == filters['bathrooms'])
        
        if filters.get('location'):
            query = query.filter(PropertyIndex.location.ilike(f"%{filters['location']}%"))
        
        if filters.get('city'):
            query = query.filter(PropertyIndex.city.ilike(f"%{filters['city']}%"))
        
        if filters.get('state'):
            query = query.filter(PropertyIndex.state.ilike(f"%{filters['state']}%"))
        
        if filters.get('property_status'):
            query = query.filter(PropertyIndex.property_status == filters['property_status'])
        
        if filters.get('amenities'):
            # Search for properties that have all specified amenities
            for amenity in filters['amenities']:
                query = query.filter(PropertyIndex.amenities.contains([amenity]))

        # Apply sorting
        sort_by = filters.get('sort_by', 'created_at')
        sort_order = filters.get('sort_order', 'desc')
        
        if sort_order.lower() == 'asc':
            query = query.order_by(getattr(PropertyIndex, sort_by).asc())
        else:
            query = query.order_by(getattr(PropertyIndex, sort_by).desc())

        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        return query.all()

    def get_property_by_id(self, post_id: int) -> Optional[PropertyIndex]:
        return self.db.query(PropertyIndex).filter(PropertyIndex.post_id == post_id).first()

    def update_property_index(self, post_id: int, update_data: Dict[str, Any]) -> Optional[PropertyIndex]:
        property_index = self.get_property_by_id(post_id)
        if property_index:
            for key, value in update_data.items():
                setattr(property_index, key, value)
            property_index.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(property_index)
        return property_index

    def delete_property_index(self, post_id: int) -> bool:
        property_index = self.get_property_by_id(post_id)
        if property_index:
            self.db.delete(property_index)
            self.db.commit()
            return True
        return False

    def log_search(self, user_id: int, search_query: Dict[str, Any], results_count: int) -> SearchHistory:
        search_history = SearchHistory(
            user_id=user_id,
            search_query=search_query,
            results_count=results_count
        )
        self.db.add(search_history)
        self.db.commit()
        self.db.refresh(search_history)
        return search_history

    def get_search_history(self, user_id: int, limit: int = 10) -> List[SearchHistory]:
        return self.db.query(SearchHistory)\
            .filter(SearchHistory.user_id == user_id)\
            .order_by(SearchHistory.created_at.desc())\
            .limit(limit)\
            .all() 
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..entity.search_entity import PropertyIndex, SearchHistory
from typing import List, Optional, Dict, Any
from datetime import datetime

class SearchRepository:
    def __init__(self, db: Session):
        self.db = db

    def index_property(self, property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            # Start with a clean transaction
            self.db.rollback()
            
            # Check if property already exists
            existing_property = self.get_property_by_id(property_data['post_id'])
            
            try:
                if existing_property:
                    # Update existing property
                    for key, value in property_data.items():
                        if key != 'post_id':  # Don't update post_id
                            setattr(existing_property, key, value)
                    existing_property.updated_at = datetime.utcnow()
                    self.db.commit()
                    self.db.refresh(existing_property)
                    result = existing_property
                else:
                    # Create new property if it doesn't exist
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
                    result = property_index

                # Convert the SQLAlchemy model to dictionary
                return {
                    "id": result.id,
                    "post_id": result.post_id,
                    "property_type": result.property_type,
                    "property_subtype": result.property_subtype,
                    "price": float(result.price) if result.price is not None else 0.0,
                    "area": float(result.area) if result.area is not None else 0.0,
                    "bedrooms": result.bedrooms if result.bedrooms is not None else 0,
                    "bathrooms": result.bathrooms if result.bathrooms is not None else 0,
                    "location": result.location,
                    "city": result.city,
                    "state": result.state,
                    "country": result.country,
                    "latitude": float(result.latitude) if result.latitude is not None else 0.0,
                    "longitude": float(result.longitude) if result.longitude is not None else 0.0,
                    "amenities": result.amenities if result.amenities is not None else [],
                    "property_status": result.property_status,
                    "created_at": result.created_at.isoformat() if result.created_at else "",
                    "updated_at": result.updated_at.isoformat() if result.updated_at else ""
                }
                
            except Exception as e:
                self.db.rollback()
                raise e
                
        except Exception as e:
            self.db.rollback()
            raise e
            
    def _convert_to_dict(self, property_index: PropertyIndex) -> Dict[str, Any]:
        """Convert a PropertyIndex object to a dictionary."""
        return {
            "id": property_index.id,
            "post_id": property_index.post_id,
            "property_type": property_index.property_type,
            "property_subtype": property_index.property_subtype,
            "price": float(property_index.price) if property_index.price is not None else 0.0,
            "area": float(property_index.area) if property_index.area is not None else 0.0,
            "bedrooms": property_index.bedrooms if property_index.bedrooms is not None else 0,
            "bathrooms": property_index.bathrooms if property_index.bathrooms is not None else 0,
            "location": property_index.location,
            "city": property_index.city,
            "state": property_index.state,
            "country": property_index.country,
            "latitude": float(property_index.latitude) if property_index.latitude is not None else 0.0,
            "longitude": float(property_index.longitude) if property_index.longitude is not None else 0.0,
            "amenities": property_index.amenities if property_index.amenities is not None else [],
            "property_status": property_index.property_status,
            "created_at": property_index.created_at.isoformat() if property_index.created_at else "",
            "updated_at": property_index.updated_at.isoformat() if property_index.updated_at else ""
        }

    def search_properties(self, filters: Dict[str, Any], limit: int = 20, offset: int = 0) -> List[PropertyIndex]:
        try:
            query = self.db.query(PropertyIndex)

            # Define valid sort columns
            valid_sort_columns = {
                'id', 'post_id', 'property_type', 'property_subtype', 'price', 
                'area', 'bedrooms', 'bathrooms', 'location', 'city', 'state', 
                'country', 'created_at', 'updated_at'
            }

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
                from sqlalchemy import text
                # Cast the amenities column to jsonb and use jsonb containment operator
                amenities_array = list(filters['amenities'])
                query = query.filter(text("amenities::jsonb ?| array[:amenities]::text[]")).params(amenities=amenities_array)

            # Apply sorting
            sort_by = filters.get('sort_by', 'created_at')
            sort_order = filters.get('sort_order', 'desc')
            
            # Validate sort_by column
            if sort_by not in valid_sort_columns:
                sort_by = 'created_at'  # Default to created_at if invalid column
            
            # Validate sort_order
            if sort_order.lower() not in ['asc', 'desc']:
                sort_order = 'desc'  # Default to descending if invalid
            
            if sort_order.lower() == 'asc':
                query = query.order_by(getattr(PropertyIndex, sort_by).asc())
            else:
                query = query.order_by(getattr(PropertyIndex, sort_by).desc())

            # Apply pagination
            query = query.offset(offset).limit(limit)
            
            return query.all()
        except Exception as e:
            self.db.rollback()
            raise e

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
        # Ensure all values in search_query are strings
        string_search_query = {k: str(v) for k, v in search_query.items()}
        
        search_history = SearchHistory(
            user_id=user_id,
            search_query=string_search_query,
            results_count=results_count
        )
        try:
            self.db.add(search_history)
            self.db.commit()
            self.db.refresh(search_history)
            return search_history
        except Exception as e:
            self.db.rollback()
            raise e

    def get_search_history(self, user_id: int, limit: int = 10) -> List[SearchHistory]:
        return self.db.query(SearchHistory)\
            .filter(SearchHistory.user_id == user_id)\
            .order_by(SearchHistory.created_at.desc())\
            .limit(limit)\
            .all() 
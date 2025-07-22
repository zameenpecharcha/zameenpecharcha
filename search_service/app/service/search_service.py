from sqlalchemy.orm import Session
from ..repository.search_repository import SearchRepository
from ..entity.search_entity import PropertyIndex, SearchHistory
from typing import List, Optional, Dict, Any
import grpc
from concurrent import futures
import os
import sys

# Add the app directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_dir)

from ..proto_files import search_pb2, search_pb2_grpc

class SearchService:
    def __init__(self, db: Session):
        self.repository = SearchRepository(db)

    def index_property(self, property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        result = self.repository.index_property(property_data)
        if result:
            # The result is already a dictionary, no need to convert
            return result
        return None

    def search_properties(self, filters: Dict[str, Any], limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        properties = self.repository.search_properties(filters, limit, offset)
        return [self._convert_to_dict(prop) for prop in properties]

    def update_property_index(self, post_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        property_index = self.repository.update_property_index(post_id, update_data)
        if property_index:
            return self._convert_to_dict(property_index)
        return None

    def delete_property_index(self, post_id: int) -> bool:
        return self.repository.delete_property_index(post_id)

    def log_search(self, user_id: int, search_query: Dict[str, Any], results_count: int) -> Dict[str, Any]:
        # Convert all values in search_query to strings before saving
        string_search_query = {k: str(v) for k, v in search_query.items()}
        search_history = self.repository.log_search(user_id, string_search_query, results_count)
        return {
            "id": search_history.id,
            "user_id": search_history.user_id,
            "search_query": string_search_query,
            "results_count": search_history.results_count,
            "created_at": search_history.created_at.isoformat()
        }

    def get_search_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        history = self.repository.get_search_history(user_id, limit)
        return [
            {
                "id": item.id,
                "user_id": item.user_id,
                "search_query": {k: str(v) for k, v in item.search_query.items()},  # Convert values to strings
                "results_count": item.results_count,
                "created_at": item.created_at.isoformat()
            }
            for item in history
        ]

    def _convert_to_dict(self, property_index: PropertyIndex) -> Dict[str, Any]:
        return {
            "id": property_index.id,
            "post_id": property_index.post_id,
            "property_type": property_index.property_type,
            "property_subtype": property_index.property_subtype,
            "price": property_index.price,
            "area": property_index.area,
            "bedrooms": property_index.bedrooms,
            "bathrooms": property_index.bathrooms,
            "location": property_index.location,
            "city": property_index.city,
            "state": property_index.state,
            "country": property_index.country,
            "latitude": property_index.latitude,
            "longitude": property_index.longitude,
            "amenities": property_index.amenities,
            "property_status": property_index.property_status,
            "created_at": property_index.created_at.isoformat(),
            "updated_at": property_index.updated_at.isoformat()
        }

class SearchServiceServicer(search_pb2_grpc.SearchServiceServicer):
    def __init__(self, db: Session):
        self.search_service = SearchService(db)

    def IndexProperty(self, request, context):
        try:
            # Ensure we have a fresh transaction
            self.search_service.repository.db.rollback()
            
            property_data = {
                "post_id": request.post_id,
                "property_type": request.property_type,
                "property_subtype": request.property_subtype,
                "price": float(request.price),
                "area": float(request.area),
                "bedrooms": int(request.bedrooms),
                "bathrooms": int(request.bathrooms),
                "location": request.location,
                "city": request.city,
                "state": request.state,
                "country": request.country,
                "latitude": float(request.latitude) if request.latitude else None,
                "longitude": float(request.longitude) if request.longitude else None,
                "amenities": list(request.amenities) if request.amenities else [],
                "property_status": request.property_status
            }

            result = self.search_service.index_property(property_data)
            
            if result:
                try:
                    # Create PropertyIndex message from the dictionary
                    property_index = search_pb2.PropertyIndex(
                        id=result["id"],
                        post_id=result["post_id"],
                        property_type=result["property_type"],
                        property_subtype=result["property_subtype"],
                        price=float(result["price"]),
                        area=float(result["area"]),
                        bedrooms=result["bedrooms"],
                        bathrooms=result["bathrooms"],
                        location=result["location"],
                        city=result["city"],
                        state=result["state"],
                        country=result["country"],
                        latitude=float(result["latitude"]),
                        longitude=float(result["longitude"]),
                        amenities=result["amenities"],
                        property_status=result["property_status"],
                        created_at=result["created_at"],
                        updated_at=result["updated_at"]
                    )
                    
                    return search_pb2.PropertyResponse(
                        success=True,
                        message="Property indexed successfully",
                        property_index=property_index
                    )
                except Exception as e:
                    return search_pb2.PropertyResponse(
                        success=False,
                        message=f"Error creating response: {str(e)}",
                        property_index=None
                    )
            
            return search_pb2.PropertyResponse(
                success=False,
                message="Failed to index property",
                property_index=None
            )
            
        except Exception as e:
            # Ensure transaction is rolled back on error
            self.search_service.repository.db.rollback()
            return search_pb2.PropertyResponse(
                success=False,
                message=f"Error indexing property: {str(e)}",
                property_index=None
            )

    def SearchProperties(self, request, context):
        try:
            filters = {
                "property_type": request.property_type if request.property_type else None,
                "property_subtype": request.property_subtype if request.property_subtype else None,
                "min_price": float(request.min_price) if request.min_price else None,
                "max_price": float(request.max_price) if request.max_price else None,
                "min_area": float(request.min_area) if request.min_area else None,
                "max_area": float(request.max_area) if request.max_area else None,
                "bedrooms": int(request.bedrooms) if request.bedrooms else None,
                "bathrooms": int(request.bathrooms) if request.bathrooms else None,
                "location": request.location if request.location else None,
                "city": request.city if request.city else None,
                "state": request.state if request.state else None,
                "property_status": request.property_status if request.property_status else None,
                "amenities": list(request.amenities) if request.amenities else None,
                "sort_by": request.sort_by if request.sort_by else "created_at",
                "sort_order": request.sort_order if request.sort_order else "desc"
            }
            
            # Remove None values
            filters = {k: v for k, v in filters.items() if v is not None}
            
            # Convert amenities to a list if it's not already
            if 'amenities' in filters and not isinstance(filters['amenities'], list):
                filters['amenities'] = [filters['amenities']]
            
            try:
                properties = self.search_service.search_properties(
                    filters,
                    request.limit if request.limit else 20,
                    request.offset if request.offset else 0
                )
                
                # Convert properties to response format
                property_list = []
                for prop in properties:
                    try:
                        prop_dict = {
                            "id": prop.id,
                            "post_id": prop.post_id,
                            "property_type": prop.property_type,
                            "property_subtype": prop.property_subtype,
                            "price": float(prop.price) if prop.price is not None else 0.0,
                            "area": float(prop.area) if prop.area is not None else 0.0,
                            "bedrooms": prop.bedrooms if prop.bedrooms is not None else 0,
                            "bathrooms": prop.bathrooms if prop.bathrooms is not None else 0,
                            "location": prop.location,
                            "city": prop.city,
                            "state": prop.state,
                            "country": prop.country,
                            "latitude": float(prop.latitude) if prop.latitude is not None else 0.0,
                            "longitude": float(prop.longitude) if prop.longitude is not None else 0.0,
                            "amenities": prop.amenities if prop.amenities is not None else [],
                            "property_status": prop.property_status,
                            "created_at": prop.created_at.isoformat() if prop.created_at else "",
                            "updated_at": prop.updated_at.isoformat() if prop.updated_at else ""
                        }
                        property_list.append(search_pb2.PropertyIndex(**prop_dict))
                    except Exception as e:
                        print(f"Error converting property to response: {str(e)}")
                        continue
                
                return search_pb2.SearchResponse(
                    success=True,
                    message="Properties retrieved successfully",
                    properties=search_pb2.PropertyList(properties=property_list)
                )
            except Exception as e:
                print(f"Error in search_properties: {str(e)}")
                return search_pb2.SearchResponse(
                    success=False,
                    message=f"Error searching properties: {str(e)}",
                    properties=search_pb2.PropertyList(properties=[])
                )
                
        except Exception as e:
            print(f"Error in SearchProperties: {str(e)}")
            return search_pb2.SearchResponse(
                success=False,
                message=f"Error processing search request: {str(e)}",
                properties=search_pb2.PropertyList(properties=[])
            )

    def UpdatePropertyIndex(self, request, context):
        property_index = self.search_service.update_property_index(
            request.post_id,
            {
                "price": request.price,
                "property_status": request.property_status,
                "amenities": list(request.amenities)
            }
        )
        if property_index:
            return search_pb2.PropertyResponse(
                success=True,
                message="Property index updated successfully",
                property_index=search_pb2.PropertyIndex(**property_index)
            )
        return search_pb2.PropertyResponse(
            success=False,
            message="Failed to update property index"
        )

    def DeletePropertyIndex(self, request, context):
        success = self.search_service.delete_property_index(request.post_id)
        return search_pb2.DeleteResponse(
            success=success,
            message="Property index deleted successfully" if success else "Failed to delete property index"
        )

    def LogSearch(self, request, context):
        search_history = self.search_service.log_search(
            request.user_id,
            {
                "property_type": request.property_type,
                "min_price": str(request.min_price),
                "max_price": str(request.max_price),
                "location": request.location
            },
            request.results_count
        )
        return search_pb2.SearchHistoryResponse(
            success=True,
            message="Search logged successfully",
            search_history=search_pb2.SearchHistory(
                id=search_history["id"],
                user_id=search_history["user_id"],
                search_query=search_history["search_query"],
                results_count=search_history["results_count"],
                created_at=search_history["created_at"]
            )
        )

    def GetSearchHistory(self, request, context):
        history = self.search_service.get_search_history(request.user_id, request.limit)
        history_list = search_pb2.SearchHistoryList(
            search_history=[
                search_pb2.SearchHistory(
                    id=item["id"],
                    user_id=item["user_id"],
                    search_query={k: str(v) for k, v in item["search_query"].items()},  # Convert all values to strings
                    results_count=item["results_count"],
                    created_at=item["created_at"]
                ) for item in history
            ]
        )
        return search_pb2.SearchHistoryListResponse(
            success=True,
            message="Search history retrieved successfully",
            search_history=history_list
        )

def serve():
    from ..utils.db_connection import get_db_session
    db = get_db_session()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    search_pb2_grpc.add_SearchServiceServicer_to_server(SearchServiceServicer(db), server)
    server.add_insecure_port('[::]:50055')
    print("Starting search service on port 50055...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve() 
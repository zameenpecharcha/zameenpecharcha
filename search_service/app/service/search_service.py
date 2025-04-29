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

from proto_files.search_pb2 import PropertyIndex as PropertyIndexProto
from proto_files import search_pb2, search_pb2_grpc

class SearchService:
    def __init__(self, db: Session):
        self.repository = SearchRepository(db)

    def index_property(self, property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        property_index = self.repository.index_property(property_data)
        if property_index:
            return self._convert_to_dict(property_index)
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
        search_history = self.repository.log_search(user_id, search_query, results_count)
        return {
            "id": search_history.id,
            "user_id": search_history.user_id,
            "search_query": search_history.search_query,
            "results_count": search_history.results_count,
            "created_at": search_history.created_at.isoformat()
        }

    def get_search_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        history = self.repository.get_search_history(user_id, limit)
        return [
            {
                "id": item.id,
                "user_id": item.user_id,
                "search_query": item.search_query,
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
        property_index = self.search_service.index_property({
            "post_id": request.post_id,
            "property_type": request.property_type,
            "property_subtype": request.property_subtype,
            "price": request.price,
            "area": request.area,
            "bedrooms": request.bedrooms,
            "bathrooms": request.bathrooms,
            "location": request.location,
            "city": request.city,
            "state": request.state,
            "country": request.country,
            "latitude": request.latitude,
            "longitude": request.longitude,
            "amenities": list(request.amenities),
            "property_status": request.property_status
        })
        if property_index:
            return search_pb2.PropertyResponse(
                success=True,
                message="Property indexed successfully",
                property_index=PropertyIndexProto(**property_index)
            )
        return search_pb2.PropertyResponse(
            success=False,
            message="Failed to index property"
        )

    def SearchProperties(self, request, context):
        filters = {
            "property_type": request.property_type,
            "property_subtype": request.property_subtype,
            "min_price": request.min_price,
            "max_price": request.max_price,
            "min_area": request.min_area,
            "max_area": request.max_area,
            "bedrooms": request.bedrooms,
            "bathrooms": request.bathrooms,
            "location": request.location,
            "city": request.city,
            "state": request.state,
            "property_status": request.property_status,
            "amenities": list(request.amenities),
            "sort_by": request.sort_by,
            "sort_order": request.sort_order
        }
        properties = self.search_service.search_properties(
            filters,
            request.limit,
            request.offset
        )
        return search_pb2.SearchResponse(
            success=True,
            message="Properties retrieved successfully",
            properties=[PropertyIndexProto(**prop) for prop in properties]
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
                property_index=PropertyIndexProto(**property_index)
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
                "min_price": request.min_price,
                "max_price": request.max_price,
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
        return search_pb2.SearchHistoryListResponse(
            success=True,
            message="Search history retrieved successfully",
            search_history=[search_pb2.SearchHistory(
                id=item["id"],
                user_id=item["user_id"],
                search_query=item["search_query"],
                results_count=item["results_count"],
                created_at=item["created_at"]
            ) for item in history]
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    search_pb2_grpc.add_SearchServiceServicer_to_server(SearchServiceServicer(), server)
    server.add_insecure_port('[::]:50055')
    print("Starting search service on port 50055...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve() 
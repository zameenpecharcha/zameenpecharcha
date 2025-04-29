from sqlalchemy.orm import Session
from ..repository.feed_repository import FeedRepository
from ..entity.feed_entity import FeedItem
from typing import List, Optional, Dict, Any
import grpc
from concurrent import futures
import os
import sys

# Add the app directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_dir)

from proto_files.feed_pb2 import FeedItem as FeedItemProto
from proto_files import feed_pb2, feed_pb2_grpc

class FeedService:
    def __init__(self, db: Session):
        self.repository = FeedRepository(db)

    def get_feed(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        feed_items = self.repository.get_feed_items(user_id, limit, offset)
        return [
            {
                "id": item.id,
                "post_id": item.post_id,
                "user_id": item.user_id,
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat()
            }
            for item in feed_items
        ]

    def add_to_feed(self, post_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        feed_item = self.repository.add_to_feed(post_id, user_id)
        if feed_item:
            return {
                "id": feed_item.id,
                "post_id": feed_item.post_id,
                "user_id": feed_item.user_id,
                "created_at": feed_item.created_at.isoformat(),
                "updated_at": feed_item.updated_at.isoformat()
            }
        return None

    def remove_from_feed(self, post_id: int, user_id: int) -> bool:
        return self.repository.remove_from_feed(post_id, user_id)

class FeedServiceServicer(feed_pb2_grpc.FeedServiceServicer):
    def __init__(self, db: Session):
        self.feed_service = FeedService(db)

    def GetFeed(self, request, context):
        feed_items = self.feed_service.get_feed(request.user_id, request.limit, request.offset)
        return feed_pb2.GetFeedResponse(
            success=True,
            message="Feed retrieved successfully",
            feed_items=[FeedItemProto(**item) for item in feed_items]
        )

    def AddToFeed(self, request, context):
        feed_item = self.feed_service.add_to_feed(request.post_id, request.user_id)
        if feed_item:
            return feed_pb2.FeedResponse(
                success=True,
                message="Added to feed successfully",
                feed_item=FeedItemProto(**feed_item)
            )
        return feed_pb2.FeedResponse(
            success=False,
            message="Failed to add to feed"
        )

    def RemoveFromFeed(self, request, context):
        success = self.feed_service.remove_from_feed(request.post_id, request.user_id)
        return feed_pb2.FeedResponse(
            success=success,
            message="Removed from feed successfully" if success else "Failed to remove from feed"
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    feed_pb2_grpc.add_FeedServiceServicer_to_server(FeedServiceServicer(), server)
    server.add_insecure_port('[::]:50053')
    print("Starting feed service on port 50053...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve() 
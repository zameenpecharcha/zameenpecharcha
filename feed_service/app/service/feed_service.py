from sqlalchemy.orm import Session
from ..repository.feed_repository import FeedRepository
from ..entity.feed_entity import FeedItem
from ..entity.post_entity import Post
from typing import List, Optional, Dict, Any
import grpc
from concurrent import futures
import os
import sys
import logging
from ..utils.db_connection import get_db_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Set up logging with debug level
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the app directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_dir)

from ..proto_files import feed_pb2, feed_pb2_grpc

class FeedService:
    def __init__(self, db: Session):
        self.repository = FeedRepository(db)

    def get_feed(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        try:
            feed_items = self.repository.get_feed_items(user_id, limit, offset)
            return [
                {
                    "id": str(item.id) if item.id else "",
                    "post_id": int(item.post_id) if item.post_id else 0,
                    "user_id": int(item.user_id) if item.user_id else 0,
                    "created_at": item.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if item.created_at else "",
                    "updated_at": item.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ") if item.updated_at else ""
                }
                for item in feed_items
            ]
        except Exception as e:
            logger.error(f"Error in get_feed: {e}")
            return []

    def add_to_feed(self, post_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        try:
            feed_item = self.repository.add_to_feed(post_id, user_id)
            if feed_item:
                return {
                    "id": str(feed_item.id) if feed_item.id else "",
                    "post_id": int(feed_item.post_id) if feed_item.post_id else 0,
                    "user_id": int(feed_item.user_id) if feed_item.user_id else 0,
                    "created_at": feed_item.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if feed_item.created_at else "",
                    "updated_at": feed_item.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ") if feed_item.updated_at else ""
                }
            return None
        except Exception as e:
            logger.error(f"Error in add_to_feed: {e}")
            return None

    def remove_from_feed(self, post_id: int, user_id: int) -> bool:
        try:
            return self.repository.remove_from_feed(post_id, user_id)
        except Exception as e:
            logger.error(f"Error in remove_from_feed: {e}")
            return False

class FeedServiceServicer(feed_pb2_grpc.FeedServiceServicer):
    def __init__(self, db_session: sessionmaker):
        self.db_session = db_session

    def GetFeed(self, request, context):
        logger.info(f"Received GetFeed request: user_id={request.user_id}, limit={request.limit}, offset={request.offset}")
        try:
            with self.db_session() as session:
                feed_service = FeedService(session)
                feed_items = feed_service.get_feed(request.user_id, request.limit, request.offset)
                logger.debug(f"Raw feed items: {feed_items}")
                
                # Convert feed items to proto format
                feed_items_proto = []
                for item in feed_items:
                    try:
                        # Validate and sanitize data
                        item_id = str(item["id"]).strip() if item.get("id") else ""
                        post_id = int(item.get("post_id", 0))
                        user_id = int(item.get("user_id", 0))
                        created_at = str(item.get("created_at", "")).strip()
                        updated_at = str(item.get("updated_at", "")).strip()

                        # Create proto message with validated data
                        feed_item_proto = feed_pb2.FeedItem(
                            id=item_id,
                            post_id=post_id,
                            user_id=user_id,
                            created_at=created_at,
                            updated_at=updated_at
                        )
                        logger.debug(f"Created feed item proto: {feed_item_proto}")
                        feed_items_proto.append(feed_item_proto)
                    except Exception as e:
                        logger.error(f"Error converting feed item: {e}, item: {item}")
                        continue

                # Create response with all fields set in constructor
                feed_items_list = feed_pb2.FeedItemList(feed_items=feed_items_proto)
                response = feed_pb2.GetFeedResponse(
                    success=True,
                    message="Feed retrieved successfully",
                    feed_items=feed_items_list
                )
                
                logger.info(f"GetFeed response: success=True, items_count={len(feed_items_proto)}")
                logger.debug(f"Full response object: {response}")
                return response

        except Exception as e:
            error_msg = f"Error retrieving feed: {str(e)}"
            logger.error(error_msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)
            empty_list = feed_pb2.FeedItemList(feed_items=[])
            return feed_pb2.GetFeedResponse(
                success=False,
                message=error_msg,
                feed_items=empty_list
            )

    def AddToFeed(self, request, context):
        logger.info(f"Received AddToFeed request: post_id={request.post_id}, user_id={request.user_id}")
        try:
            with self.db_session() as session:
                feed_service = FeedService(session)
                post_id = request.post_id
                user_id = request.user_id
                feed_item = feed_service.add_to_feed(post_id, user_id)
                
                if feed_item:
                    feed_item_proto = feed_pb2.FeedItem(
                        id=str(feed_item["id"]),
                        post_id=feed_item["post_id"],
                        user_id=feed_item["user_id"],
                        created_at=feed_item["created_at"],
                        updated_at=feed_item["updated_at"]
                    )
                    
                    response = feed_pb2.FeedResponse(
                        success=True,
                        message="Added to feed successfully",
                        feed_item=feed_item_proto
                    )
                    logger.info("AddToFeed response: success=True")
                    return response
                
                logger.warning("AddToFeed failed: feed_item is None")
                return feed_pb2.FeedResponse(
                    success=False,
                    message="Failed to add to feed",
                    feed_item=None
                )
                
        except Exception as e:
            error_msg = f"Error adding to feed: {str(e)}"
            logger.error(error_msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)
            return feed_pb2.FeedResponse(
                success=False,
                message=error_msg,
                feed_item=None
            )

    def RemoveFromFeed(self, request, context):
        logger.info(f"Received RemoveFromFeed request: post_id={request.post_id}, user_id={request.user_id}")
        try:
            with self.db_session() as session:
                feed_service = FeedService(session)
                post_id = request.post_id
                user_id = request.user_id
                success = feed_service.remove_from_feed(post_id, user_id)
                logger.info(f"RemoveFromFeed response: success={success}")
                return feed_pb2.FeedResponse(
                    success=success,
                    message="Removed from feed successfully" if success else "Failed to remove from feed"
                )
        except Exception as e:
            error_msg = f"Error removing from feed: {str(e)}"
            logger.error(error_msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)
            return feed_pb2.FeedResponse(
                success=False,
                message=error_msg
            )

def serve():
    # Initialize database connection
    engine = get_db_engine()
    SessionLocal = sessionmaker(bind=engine)
    
    # Create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    feed_pb2_grpc.add_FeedServiceServicer_to_server(FeedServiceServicer(SessionLocal), server)
    port = 50056
    server.add_insecure_port(f'[::]:{port}')
    logger.info(f"Starting feed service on port {port}...")
    server.start()
    logger.info("Feed service is running...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve() 
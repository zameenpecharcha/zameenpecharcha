from sqlalchemy.orm import Session
from ..repository.trending_repository import TrendingRepository
from ..entity.trending_entity import TrendingPost
from typing import List, Optional, Dict, Any
import grpc
from concurrent import futures
import os
import sys
import threading
import time

# Add the app directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_dir)

from app.proto_files.trending_pb2 import TrendingPost as TrendingPostProto
from app.proto_files import trending_pb2, trending_pb2_grpc

class TrendingService:
    def __init__(self, db: Session):
        self.repository = TrendingRepository(db)
        self._start_rank_updater()

    def _start_rank_updater(self):
        def update_ranks_periodically():
            while True:
                self.repository.update_ranks()
                time.sleep(300)  # Update ranks every 5 minutes

        thread = threading.Thread(target=update_ranks_periodically, daemon=True)
        thread.start()

    def update_post_metrics(self, post_id: int, like_count: int, comment_count: int) -> Optional[Dict[str, Any]]:
        trending_post = self.repository.update_trending_posts(post_id, like_count, comment_count)
        if trending_post:
            return {
                "id": trending_post.id,
                "post_id": trending_post.post_id,
                "score": trending_post.score,
                "rank": trending_post.rank,
                "created_at": trending_post.created_at.isoformat(),
                "updated_at": trending_post.updated_at.isoformat()
            }
        return None

    def get_trending_posts(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        trending_posts = self.repository.get_trending_posts(limit, offset)
        return [
            {
                "id": post.id,
                "post_id": post.post_id,
                "score": post.score,
                "rank": post.rank,
                "created_at": post.created_at.isoformat(),
                "updated_at": post.updated_at.isoformat()
            }
            for post in trending_posts
        ]

    def get_post_rank(self, post_id: int) -> Optional[int]:
        return self.repository.get_post_rank(post_id)

class TrendingServiceServicer(trending_pb2_grpc.TrendingServiceServicer):
    def __init__(self, db: Session):
        self.trending_service = TrendingService(db)

    def UpdatePostMetrics(self, request, context):
        trending_post = self.trending_service.update_post_metrics(
            request.post_id,
            request.like_count,
            request.comment_count
        )
        if trending_post:
            return trending_pb2.TrendingResponse(
                success=True,
                message="Post metrics updated successfully",
                trending_post=TrendingPostProto(**trending_post)
            )
        return trending_pb2.TrendingResponse(
            success=False,
            message="Failed to update post metrics"
        )

    def GetTrendingPosts(self, request, context):
        try:
            # Validate and sanitize parameters
            limit = max(1, min(request.limit if request.limit > 0 else 20, 100))  # Between 1 and 100, default 20
            offset = max(0, request.offset if request.offset >= 0 else 0)  # Non-negative, default 0
            
            trending_posts = self.trending_service.get_trending_posts(limit, offset)
            trending_post_protos = []
            
            for post in trending_posts:
                trending_post_proto = trending_pb2.TrendingPost(
                    id=post["id"],
                    post_id=post["post_id"],
                    score=float(post["score"]),
                    rank=post["rank"],
                    created_at=post["created_at"],
                    updated_at=post["updated_at"]
                )
                trending_post_protos.append(trending_post_proto)
            
            trending_post_list = trending_pb2.TrendingPostList(trending_posts=trending_post_protos)
            
            return trending_pb2.GetTrendingResponse(
                success=True,
                message="Trending posts retrieved successfully",
                trending_posts=trending_post_list
            )
        except Exception as e:
            print(f"Error in GetTrendingPosts: {str(e)}")
            return trending_pb2.GetTrendingResponse(
                success=False,
                message=f"Error retrieving trending posts: {str(e)}",
                trending_posts=trending_pb2.TrendingPostList(trending_posts=[])
            )

    def GetPostRank(self, request, context):
        rank = self.trending_service.get_post_rank(request.post_id)
        return trending_pb2.RankResponse(
            success=True,
            message="Post rank retrieved successfully",
            rank=rank if rank is not None else 0
        )

def serve():
    from ..utils.db_connection import get_db_session
    db = get_db_session()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    trending_pb2_grpc.add_TrendingServiceServicer_to_server(TrendingServiceServicer(db), server)
    server.add_insecure_port('[::]:50054')
    print("Starting trending service on port 50054...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve() 
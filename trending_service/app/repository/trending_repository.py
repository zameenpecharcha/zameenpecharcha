from sqlalchemy.orm import Session
from ..entity.trending_entity import TrendingPost
from typing import List, Optional
from datetime import datetime, timedelta

class TrendingRepository:
    def __init__(self, db: Session):
        self.db = db

    def calculate_score(self, like_count: int, comment_count: int, time_factor: float) -> float:
        # Score calculation formula:
        # Base score = (likes * 2) + (comments * 1.5)
        # Time decay factor = 1 / (1 + hours_since_creation)
        base_score = (like_count * 2) + (comment_count * 1.5)
        return base_score * time_factor

    def update_trending_posts(self, post_id: int, like_count: int, comment_count: int) -> Optional[TrendingPost]:
        # Get the post's creation time
        post = self.db.query(TrendingPost).filter(TrendingPost.post_id == post_id).first()
        
        if not post:
            # Create new trending post entry
            hours_since_creation = 0
            time_factor = 1.0
        else:
            # Calculate time factor for existing post
            hours_since_creation = (datetime.utcnow() - post.created_at).total_seconds() / 3600
            time_factor = 1.0 / (1.0 + hours_since_creation)

        score = self.calculate_score(like_count, comment_count, time_factor)

        if post:
            post.score = score
            post.updated_at = datetime.utcnow()
        else:
            post = TrendingPost(
                post_id=post_id,
                score=score,
                rank=0,  # Will be updated in update_ranks
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(post)

        self.db.commit()
        self.db.refresh(post)
        return post

    def get_trending_posts(self, limit: int = 20, offset: int = 0) -> List[TrendingPost]:
        return self.db.query(TrendingPost)\
            .order_by(TrendingPost.score.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()

    def update_ranks(self) -> None:
        # Get all trending posts ordered by score
        posts = self.db.query(TrendingPost)\
            .order_by(TrendingPost.score.desc())\
            .all()
        
        # Update ranks
        for rank, post in enumerate(posts, 1):
            post.rank = rank
        
        self.db.commit()

    def get_post_rank(self, post_id: int) -> Optional[int]:
        post = self.db.query(TrendingPost)\
            .filter(TrendingPost.post_id == post_id)\
            .first()
        return post.rank if post else None 
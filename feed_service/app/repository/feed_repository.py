from sqlalchemy.orm import Session
from ..entity.feed_entity import FeedItem
from typing import List, Optional
from datetime import datetime

class FeedRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_feed_items(self, user_id: int, limit: int = 20, offset: int = 0) -> List[FeedItem]:
        return self.db.query(FeedItem)\
            .filter(FeedItem.user_id == user_id)\
            .order_by(FeedItem.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()

    def add_to_feed(self, post_id: int, user_id: int) -> Optional[FeedItem]:
        feed_item = FeedItem(
            post_id=post_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(feed_item)
        self.db.commit()
        self.db.refresh(feed_item)
        return feed_item

    def remove_from_feed(self, post_id: int, user_id: int) -> bool:
        feed_item = self.db.query(FeedItem)\
            .filter(FeedItem.post_id == post_id, FeedItem.user_id == user_id)\
            .first()
        
        if feed_item:
            self.db.delete(feed_item)
            self.db.commit()
            return True
        return False 
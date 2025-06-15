from sqlalchemy.orm import Session
from ..entity.feed_entity import FeedItem
from ..entity.post_entity import Post
from typing import List, Optional
from datetime import datetime

class FeedRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_feed_items(self, user_id: int, limit: int = 20, offset: int = 0) -> List[FeedItem]:
        try:
            items = self.db.query(FeedItem)\
                .filter(FeedItem.user_id == user_id)\
                .order_by(FeedItem.created_at.desc())\
                .offset(offset)\
                .limit(limit)\
                .all()
            return items if items else []
        except Exception as e:
            print(f"Error in get_feed_items: {e}")
            return []

    def add_to_feed(self, post_id: int, user_id: int) -> Optional[FeedItem]:
        try:
            feed_item = FeedItem(
                post_id=post_id,
                user_id=user_id
            )
            self.db.add(feed_item)
            self.db.commit()
            self.db.refresh(feed_item)
            return feed_item
        except Exception as e:
            print(f"Error in add_to_feed: {e}")
            self.db.rollback()
            return None

    def remove_from_feed(self, post_id: int, user_id: int) -> bool:
        try:
            result = self.db.query(FeedItem)\
                .filter(FeedItem.post_id == post_id, FeedItem.user_id == user_id)\
                .delete()
            self.db.commit()
            return result > 0
        except Exception as e:
            print(f"Error in remove_from_feed: {e}")
            self.db.rollback()
            return False 
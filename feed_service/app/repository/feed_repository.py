from sqlalchemy.orm import Session
from ..entity.feed_entity import FeedItem
from ..entity.post_entity import Post
from typing import List, Optional
from datetime import datetime
import logging
from sqlalchemy import desc, and_

# Set up logging
logger = logging.getLogger(__name__)

class FeedRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_feed_items(self, user_id: int, limit: int = 20, offset: int = 0) -> List[FeedItem]:
        """Get feed items for a user with pagination"""
        try:
            items = self.db.query(FeedItem)\
                .filter(FeedItem.user_id == user_id)\
                .order_by(desc(FeedItem.created_at))\
                .offset(offset)\
                .limit(limit)\
                .all()
            return items if items else []
        except Exception as e:
            logger.error(f"Error in get_feed_items: {e}")
            return []

    def get_feed_item(self, post_id: int, user_id: int) -> Optional[FeedItem]:
        """Get a specific feed item"""
        try:
            return self.db.query(FeedItem)\
                .filter(
                    and_(
                        FeedItem.post_id == post_id,
                        FeedItem.user_id == user_id
                    )
                )\
                .first()
        except Exception as e:
            logger.error(f"Error in get_feed_item: {e}")
            return None

    def add_to_feed(self, post_id: int, user_id: int) -> Optional[FeedItem]:
        """Add a new item to user's feed"""
        try:
            # Check if item already exists
            existing_item = self.get_feed_item(post_id, user_id)
            if existing_item:
                return existing_item

            # Create new feed item
            feed_item = FeedItem(
                post_id=post_id,
                user_id=user_id,
                created_at=datetime.utcnow()
            )
            self.db.add(feed_item)
            self.db.commit()
            self.db.refresh(feed_item)
            return feed_item
        except Exception as e:
            logger.error(f"Error in add_to_feed: {e}")
            self.db.rollback()
            return None

    def remove_from_feed(self, post_id: int, user_id: int) -> bool:
        """Remove an item from user's feed"""
        try:
            result = self.db.query(FeedItem)\
                .filter(
                    and_(
                        FeedItem.post_id == post_id,
                        FeedItem.user_id == user_id
                    )
                )\
                .delete(synchronize_session=False)
            self.db.commit()
            return result > 0
        except Exception as e:
            logger.error(f"Error in remove_from_feed: {e}")
            self.db.rollback()
            return False

    def bulk_add_to_feed(self, items: List[dict]) -> List[FeedItem]:
        """Add multiple items to feed at once"""
        try:
            feed_items = [
                FeedItem(
                    post_id=item['post_id'],
                    user_id=item['user_id'],
                    created_at=datetime.utcnow()
                )
                for item in items
            ]
            self.db.bulk_save_objects(feed_items)
            self.db.commit()
            return feed_items
        except Exception as e:
            logger.error(f"Error in bulk_add_to_feed: {e}")
            self.db.rollback()
            return [] 
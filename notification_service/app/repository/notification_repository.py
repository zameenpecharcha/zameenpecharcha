from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..entity.notification import Notification, LocationSubscription
from typing import List, Optional, Tuple
from sqlalchemy import func
import json
import math
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(self, user_id: int, type: str, message: str, 
                          entity_id: int, entity_type: str, context: dict = None) -> Notification:
        try:
            notification = Notification(
                user_id=user_id,
                type=type,
                message=message,
                entity_id=entity_id,
                entity_type=entity_type,
                context=json.dumps(context) if context else None
            )
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
            return notification
        except SQLAlchemyError as e:
            logger.error(f"Error creating notification: {str(e)}")
            self.db.rollback()
            raise

    def get_user_notifications(self, user_id: int, page: int = 1, 
                             page_size: int = 10, unread_only: bool = False) -> Tuple[List[Notification], int, int]:
        try:
            query = self.db.query(Notification).filter(Notification.user_id == user_id)
            
            if unread_only:
                query = query.filter(Notification.is_read == False)
            
            total = query.count()
            unread_count = self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            ).count()
            
            notifications = query.order_by(Notification.created_at.desc())\
                               .offset((page - 1) * page_size)\
                               .limit(page_size)\
                               .all()
            
            return notifications, total, unread_count
        except SQLAlchemyError as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            raise

    def mark_notification_as_read(self, notification_id: int, user_id: int) -> bool:
        try:
            notification = self.db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            ).first()
            
            if notification:
                notification.is_read = True
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            self.db.rollback()
            raise

    def create_location_subscription(self, user_id: int, latitude: float, 
                                   longitude: float, radius_km: float) -> LocationSubscription:
        try:
            subscription = LocationSubscription(
                user_id=user_id,
                latitude=latitude,
                longitude=longitude,
                radius_km=radius_km
            )
            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)
            return subscription
        except SQLAlchemyError as e:
            logger.error(f"Error creating location subscription: {str(e)}")
            self.db.rollback()
            raise

    def get_user_subscriptions(self, user_id: int) -> List[LocationSubscription]:
        try:
            return self.db.query(LocationSubscription)\
                         .filter(LocationSubscription.user_id == user_id)\
                         .all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user subscriptions: {str(e)}")
            raise

    def delete_subscription(self, subscription_id: int, user_id: int) -> bool:
        try:
            subscription = self.db.query(LocationSubscription).filter(
                LocationSubscription.id == subscription_id,
                LocationSubscription.user_id == user_id
            ).first()
            
            if subscription:
                self.db.delete(subscription)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting subscription: {str(e)}")
            self.db.rollback()
            raise

    def get_subscribers_near_location(self, latitude: float, longitude: float, 
                                    radius_km: float) -> List[LocationSubscription]:
        try:
            # Using a simple bounding box approximation for initial filtering
            # This could be optimized with PostGIS or similar for production
            lat_range = radius_km / 111.32  # Approximate km per degree of latitude
            lon_range = radius_km / (111.32 * abs(math.cos(math.radians(latitude))))
            
            min_lat = latitude - lat_range
            max_lat = latitude + lat_range
            min_lon = longitude - lon_range
            max_lon = longitude + lon_range
            
            return self.db.query(LocationSubscription)\
                         .filter(
                             LocationSubscription.latitude.between(min_lat, max_lat),
                             LocationSubscription.longitude.between(min_lon, max_lon),
                             LocationSubscription.is_active == True
                         )\
                         .all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting subscribers near location: {str(e)}")
            raise 
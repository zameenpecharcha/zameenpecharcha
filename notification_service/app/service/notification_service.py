import grpc
from concurrent import futures
import os
import sys
from sqlalchemy.orm import Session
from ..repository.notification_repository import NotificationRepository
from ..entity.notification import Notification, LocationSubscription
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

# Add the app directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_dir)

from proto_files.notification_pb2 import (
    Notification as ProtoNotification,
    LocationSubscription as ProtoLocationSubscription,
    GetUserNotificationsRequest,
    GetUserNotificationsResponse,
    MarkNotificationAsReadRequest,
    MarkNotificationAsReadResponse,
    SubscribeToLocationRequest,
    SubscribeToLocationResponse,
    UnsubscribeFromLocationRequest,
    UnsubscribeFromLocationResponse,
    GetUserSubscriptionsRequest,
    GetUserSubscriptionsResponse,
    CreatePostLikeNotificationRequest,
    CreatePostCommentNotificationRequest,
    CreateCommentLikeNotificationRequest,
    CreateCommentReplyNotificationRequest,
    CreateTrendingPostNotificationRequest,
    NotifyTrendingPostsRequest,
    NotifyTrendingPostsResponse
)
from proto_files import notification_pb2_grpc

class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    def create_notification(self, user_id: int, type: str, message: str, 
                          entity_id: int, entity_type: str, context: Dict[str, Any] = None) -> Notification:
        """Create a new notification for a user."""
        return self.repository.create_notification(
            user_id=user_id,
            type=type,
            message=message,
            entity_id=entity_id,
            entity_type=entity_type,
            context=context
        )

    def get_user_notifications(self, user_id: int, page: int = 1, 
                             page_size: int = 10, unread_only: bool = False) -> Dict[str, Any]:
        """Get notifications for a user with pagination and unread status filter."""
        notifications, total, unread_count = self.repository.get_user_notifications(
            user_id=user_id,
            page=page,
            page_size=page_size,
            unread_only=unread_only
        )
        
        return {
            "notifications": notifications,
            "total": total,
            "unread_count": unread_count,
            "page": page,
            "page_size": page_size
        }

    def mark_notification_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a specific notification as read."""
        return self.repository.mark_notification_as_read(notification_id, user_id)

    def create_location_subscription(self, user_id: int, latitude: float, 
                                   longitude: float, radius_km: float) -> LocationSubscription:
        """Create a new location subscription for a user."""
        return self.repository.create_location_subscription(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )

    def get_user_subscriptions(self, user_id: int) -> List[LocationSubscription]:
        """Get all location subscriptions for a user."""
        return self.repository.get_user_subscriptions(user_id)

    def delete_subscription(self, subscription_id: int, user_id: int) -> bool:
        """Delete a location subscription."""
        return self.repository.delete_subscription(subscription_id, user_id)

    def notify_post_like(self, post_id: int, post_owner_id: int, liker_id: int) -> Notification:
        """Create a notification for a post like."""
        return self.create_notification(
            user_id=post_owner_id,
            type="post_like",
            message=f"Someone liked your post",
            entity_id=post_id,
            entity_type="post",
            context={"liker_id": liker_id}
        )

    def notify_comment(self, post_id: int, post_owner_id: int, comment_id: int, 
                      commenter_id: int) -> Notification:
        """Create a notification for a new comment."""
        return self.create_notification(
            user_id=post_owner_id,
            type="comment",
            message=f"Someone commented on your post",
            entity_id=post_id,
            entity_type="post",
            context={
                "comment_id": comment_id,
                "commenter_id": commenter_id
            }
        )

    def notify_trending_post(self, post_id: int, latitude: float, longitude: float) -> List[Notification]:
        """Create notifications for users subscribed to a location about a trending post."""
        subscribers = self.repository.get_subscribers_near_location(
            latitude=latitude,
            longitude=longitude,
            radius_km=5.0  # Default radius for trending notifications
        )
        
        notifications = []
        for subscriber in subscribers:
            notification = self.create_notification(
                user_id=subscriber.user_id,
                type="trending_post",
                message="A new trending post is available in your area",
                entity_id=post_id,
                entity_type="post",
                context={
                    "latitude": latitude,
                    "longitude": longitude
                }
            )
            notifications.append(notification)
        
        return notifications

class NotificationServiceServicer(notification_pb2_grpc.NotificationServiceServicer):
    def __init__(self):
        from ..database import SessionLocal
        self.db = SessionLocal()
        self.service = NotificationService(self.db)

    def GetUserNotifications(self, request, context):
        notifications = self.service.get_user_notifications(
            request.user_id,
            request.page,
            request.page_size,
            request.unread_only
        )
        
        proto_notifications = []
        for notification in notifications:
            proto_notifications.append(ProtoNotification(
                id=notification.id,
                user_id=notification.user_id,
                type=notification.type,
                message=notification.message,
                entity_id=notification.entity_id,
                entity_type=notification.entity_type,
                is_read=notification.is_read,
                created_at=notification.created_at.isoformat(),
                context=notification.context or ""
            ))
        
        return GetUserNotificationsResponse(
            notifications=proto_notifications,
            total_count=len(notifications),
            unread_count=sum(1 for n in notifications if not n.is_read)
        )

    def MarkNotificationAsRead(self, request, context):
        success = self.service.mark_notification_as_read(
            request.notification_id,
            request.user_id
        )
        return MarkNotificationAsReadResponse(success=success)

    def SubscribeToLocation(self, request, context):
        subscription = self.service.create_location_subscription(
            request.user_id,
            request.latitude,
            request.longitude,
            request.radius_km
        )
        
        return SubscribeToLocationResponse(
            subscription=ProtoLocationSubscription(
                id=subscription.id,
                user_id=subscription.user_id,
                latitude=subscription.latitude,
                longitude=subscription.longitude,
                radius_km=subscription.radius_km,
                created_at=subscription.created_at.isoformat(),
                is_active=subscription.is_active
            )
        )

    def UnsubscribeFromLocation(self, request, context):
        success = self.service.delete_subscription(
            request.subscription_id,
            request.user_id
        )
        return UnsubscribeFromLocationResponse(success=success)

    def GetUserSubscriptions(self, request, context):
        subscriptions = self.service.get_user_subscriptions(request.user_id)
        
        proto_subscriptions = []
        for subscription in subscriptions:
            proto_subscriptions.append(ProtoLocationSubscription(
                id=subscription.id,
                user_id=subscription.user_id,
                latitude=subscription.latitude,
                longitude=subscription.longitude,
                radius_km=subscription.radius_km,
                created_at=subscription.created_at.isoformat(),
                is_active=subscription.is_active
            ))
        
        return GetUserSubscriptionsResponse(subscriptions=proto_subscriptions)

    def CreatePostLikeNotification(self, request, context):
        notification = self.service.notify_post_like(
            request.post_id,
            request.post_owner_id,
            request.liker_id
        )
        
        return ProtoNotification(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            message=notification.message,
            entity_id=notification.entity_id,
            entity_type=notification.entity_type,
            is_read=notification.is_read,
            created_at=notification.created_at.isoformat(),
            context=notification.context or ""
        )

    def CreatePostCommentNotification(self, request, context):
        notification = self.service.notify_comment(
            request.post_id,
            request.post_owner_id,
            request.comment_id,
            request.commenter_id
        )
        
        return ProtoNotification(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            message=notification.message,
            entity_id=notification.entity_id,
            entity_type=notification.entity_type,
            is_read=notification.is_read,
            created_at=notification.created_at.isoformat(),
            context=notification.context or ""
        )

    def CreateCommentLikeNotification(self, request, context):
        notification = self.service.create_notification(
            request.comment_owner_id,
            "comment_like",
            f"User {request.liker_id} liked your comment",
            request.comment_id,
            "comment"
        )
        
        return ProtoNotification(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            message=notification.message,
            entity_id=notification.entity_id,
            entity_type=notification.entity_type,
            is_read=notification.is_read,
            created_at=notification.created_at.isoformat(),
            context=notification.context or ""
        )

    def CreateCommentReplyNotification(self, request, context):
        notification = self.service.create_notification(
            request.comment_owner_id,
            "comment_reply",
            f"User {request.replier_id} replied to your comment",
            request.comment_id,
            "comment",
            request.reply_text
        )
        
        return ProtoNotification(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            message=notification.message,
            entity_id=notification.entity_id,
            entity_type=notification.entity_type,
            is_read=notification.is_read,
            created_at=notification.created_at.isoformat(),
            context=notification.context or ""
        )

    def CreateTrendingPostNotification(self, request, context):
        notification = self.service.create_notification(
            request.user_id,
            "trending_post",
            f"Trending post in {request.location_name}",
            request.post_id,
            "post",
            request.location_name
        )
        
        return ProtoNotification(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            message=notification.message,
            entity_id=notification.entity_id,
            entity_type=notification.entity_type,
            is_read=notification.is_read,
            created_at=notification.created_at.isoformat(),
            context=notification.context or ""
        )

    def NotifyTrendingPosts(self, request, context):
        notifications = self.service.notify_trending_post(
            request.post_id,
            request.latitude,
            request.longitude
        )
        
        proto_notifications = []
        for notification in notifications:
            proto_notifications.append(ProtoNotification(
                id=notification.id,
                user_id=notification.user_id,
                type=notification.type,
                message=notification.message,
                entity_id=notification.entity_id,
                entity_type=notification.entity_type,
                is_read=notification.is_read,
                created_at=notification.created_at.isoformat(),
                context=notification.context or ""
            ))
        
        return NotifyTrendingPostsResponse(
            notifications=proto_notifications,
            total_notified=len(notifications)
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notification_pb2_grpc.add_NotificationServiceServicer_to_server(
        NotificationServiceServicer(), server)
    server.add_insecure_port('[::]:50057')
    print("Starting notification service on port 50057...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve() 
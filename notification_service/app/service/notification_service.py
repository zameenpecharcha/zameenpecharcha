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

from app.proto_files.notification_pb2 import (
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
from app.proto_files import notification_pb2_grpc

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
            message=f"User {liker_id} liked your post",
            entity_id=post_id,
            entity_type="post",
            context={"liker_id": liker_id}
        )

    def notify_comment(self, post_id: int, post_owner_id: int, commenter_id: int, comment_text: str) -> Notification:
        """Create a notification for a new comment."""
        return self.create_notification(
            user_id=post_owner_id,
            type="comment",
            message=f"User {commenter_id} commented on your post",
            entity_id=post_id,
            entity_type="post",
            context={
                "commenter_id": commenter_id,
                "comment_text": comment_text
            }
        )

    def notify_comment_like(self, comment_id: int, comment_owner_id: int, liker_id: int) -> Notification:
        """Create a notification for a comment like."""
        return self.create_notification(
            user_id=comment_owner_id,
            type="comment_like",
            message=f"User {liker_id} liked your comment",
            entity_id=comment_id,
            entity_type="comment",
            context={"liker_id": liker_id}
        )

    def notify_comment_reply(self, comment_id: int, comment_owner_id: int, replier_id: int, reply_text: str) -> Notification:
        """Create a notification for a comment reply."""
        return self.create_notification(
            user_id=comment_owner_id,
            type="comment_reply",
            message=f"User {replier_id} replied to your comment",
            entity_id=comment_id,
            entity_type="comment",
            context={
                "replier_id": replier_id,
                "reply_text": reply_text
            }
        )

    def notify_trending_post(self, post_id: int, latitude: float, longitude: float, radius_km: float, location_name: str) -> List[Notification]:
        """Create notifications for users subscribed to a location about a trending post."""
        subscribers = self.repository.get_subscribers_near_location(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )
        
        notifications = []
        for subscriber in subscribers:
            notification = self.create_notification(
                user_id=subscriber.user_id,
                type="trending_post",
                message=f"A post is trending in {location_name}",
                entity_id=post_id,
                entity_type="post",
                context={
                    "latitude": latitude,
                    "longitude": longitude,
                    "location_name": location_name
                }
            )
            notifications.append(notification)
        
        return notifications

class NotificationServiceServicer(notification_pb2_grpc.NotificationServiceServicer):
    def __init__(self, db: Session):
        self.service = NotificationService(NotificationRepository(db))

    def GetUserNotifications(self, request, context):
        try:
            result = self.service.get_user_notifications(
                user_id=request.user_id,
                page=request.page,
                page_size=request.page_size,
                unread_only=request.unread_only
            )
            
            proto_notifications = []
            for notification in result["notifications"]:
                context_str = notification.context if isinstance(notification.context, str) else json.dumps(notification.context) if notification.context else ""
                proto_notifications.append(ProtoNotification(
                    id=notification.id,
                    user_id=notification.user_id,
                    type=notification.type,
                    message=notification.message,
                    entity_id=notification.entity_id,
                    entity_type=notification.entity_type,
                    is_read=notification.is_read,
                    created_at=notification.created_at.isoformat(),
                    context=context_str
                ))
            
            return GetUserNotificationsResponse(
                notifications=proto_notifications,
                total_count=result["total"],
                unread_count=result["unread_count"]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return GetUserNotificationsResponse()

    def MarkNotificationAsRead(self, request, context):
        try:
            success = self.service.mark_notification_as_read(
                request.notification_id,
                request.user_id
            )
            return MarkNotificationAsReadResponse(success=success)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return MarkNotificationAsReadResponse(success=False)

    def SubscribeToLocation(self, request, context):
        try:
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
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return SubscribeToLocationResponse()

    def UnsubscribeFromLocation(self, request, context):
        try:
            success = self.service.delete_subscription(
                request.subscription_id,
                request.user_id
            )
            return UnsubscribeFromLocationResponse(success=success)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return UnsubscribeFromLocationResponse(success=False)

    def GetUserSubscriptions(self, request, context):
        try:
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
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return GetUserSubscriptionsResponse()

    def CreatePostLikeNotification(self, request, context):
        try:
            notification = self.service.notify_post_like(
                request.post_id,
                request.post_owner_id,
                request.liker_id
            )
            
            return self._notification_to_proto(notification)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ProtoNotification()

    def CreatePostCommentNotification(self, request, context):
        try:
            notification = self.service.notify_comment(
                request.post_id,
                request.post_owner_id,
                request.commenter_id,
                request.comment_text
            )
            
            return self._notification_to_proto(notification)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ProtoNotification()

    def CreateCommentLikeNotification(self, request, context):
        try:
            notification = self.service.notify_comment_like(
                request.comment_id,
                request.comment_owner_id,
                request.liker_id
            )
            
            return self._notification_to_proto(notification)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ProtoNotification()

    def CreateCommentReplyNotification(self, request, context):
        try:
            notification = self.service.notify_comment_reply(
                request.comment_id,
                request.comment_owner_id,
                request.replier_id,
                request.reply_text
            )
            
            return self._notification_to_proto(notification)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ProtoNotification()

    def CreateTrendingPostNotification(self, request, context):
        try:
            notification = self.service.create_notification(
                request.user_id,
                "trending_post",
                f"A post is trending in {request.location_name}",
                request.post_id,
                "post",
                {"location_name": request.location_name}
            )
            
            return self._notification_to_proto(notification)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ProtoNotification()

    def NotifyTrendingPosts(self, request, context):
        try:
            notifications = self.service.notify_trending_post(
                request.post_id,
                request.latitude,
                request.longitude,
                request.radius_km,
                request.location_name
            )
            
            proto_notifications = [self._notification_to_proto(n) for n in notifications]
            
            return NotifyTrendingPostsResponse(
                notifications=proto_notifications,
                total_notified=len(notifications)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return NotifyTrendingPostsResponse()

    def _notification_to_proto(self, notification: Notification) -> ProtoNotification:
        """Helper method to convert Notification model to Proto message."""
        context_str = notification.context if isinstance(notification.context, str) else json.dumps(notification.context) if notification.context else ""
        return ProtoNotification(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            message=notification.message,
            entity_id=notification.entity_id,
            entity_type=notification.entity_type,
            is_read=notification.is_read,
            created_at=notification.created_at.isoformat(),
            context=context_str
        )

def serve():
    from ..utils.database import SessionLocal
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notification_pb2_grpc.add_NotificationServiceServicer_to_server(
        NotificationServiceServicer(SessionLocal()), server)
    server.add_insecure_port('localhost:50056')
    print("Starting notification service on port 50056...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve() 
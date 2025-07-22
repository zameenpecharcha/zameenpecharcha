from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.service.notification_service import NotificationService
from typing import List
from pydantic import BaseModel

router = APIRouter()

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    message: str
    entity_id: int
    entity_type: str
    is_read: bool
    created_at: str
    context: str = None

    class Config:
        orm_mode = True

class LocationSubscriptionRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float

class LocationSubscriptionResponse(BaseModel):
    id: int
    user_id: int
    latitude: float
    longitude: float
    radius_km: float
    created_at: str
    is_active: bool

    class Config:
        orm_mode = True

@router.get("/", response_model=List[NotificationResponse])
def get_user_notifications(
    user_id: int,
    page: int = 1,
    page_size: int = 10,
    unread_only: bool = False,
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    return service.get_user_notifications(user_id, page, page_size, unread_only)

@router.post("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    success = service.mark_notification_as_read(notification_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "success"}

@router.post("/subscribe", response_model=LocationSubscriptionResponse)
def subscribe_to_location(
    user_id: int,
    subscription: LocationSubscriptionRequest,
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    return service.subscribe_to_location(
        user_id,
        subscription.latitude,
        subscription.longitude,
        subscription.radius_km
    )

@router.delete("/subscribe/{subscription_id}")
def unsubscribe_from_location(
    subscription_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    success = service.unsubscribe_from_location(subscription_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"status": "success"}

@router.get("/subscriptions", response_model=List[LocationSubscriptionResponse])
def get_user_subscriptions(
    user_id: int,
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    return service.get_user_subscriptions(user_id) 
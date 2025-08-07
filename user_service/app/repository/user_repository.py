from sqlalchemy.orm import sessionmaker
from app.utils.db_connection import get_db_engine
from sqlalchemy import select, and_
from app.entity.user_entity import users, ratings, followers, media

SessionLocal = sessionmaker(bind=get_db_engine())

class UserRow:
    def __init__(self, id, first_name, last_name, email, phone, role, address, 
                 latitude, longitude, bio, password, isactive, email_verified, phone_verified, 
                 gst_no, cover_photo_id, profile_photo_id, last_login_at, created_at):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.role = role
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.bio = bio
        self.password = password
        self.isactive = isactive
        self.email_verified = email_verified
        self.phone_verified = phone_verified
        self.gst_no = gst_no
        self.cover_photo_id = cover_photo_id
        self.profile_photo_id = profile_photo_id
        self.last_login_at = last_login_at
        self.created_at = created_at

class RatingRow:
    def __init__(self, id, rated_user_id, rated_by_user_id, rating_value, title,
                 review, rating_type, is_anonymous, created_at, updated_at):
        self.id = id
        self.rated_user_id = rated_user_id
        self.rated_by_user_id = rated_by_user_id
        self.rating_value = rating_value
        self.title = title
        self.review = review
        self.rating_type = rating_type
        self.is_anonymous = is_anonymous
        self.created_at = created_at
        self.updated_at = updated_at

class FollowerRow:
    def __init__(self, id, follower_id, following_id, followee_type, status, followed_at):
        self.id = id
        self.follower_id = follower_id
        self.following_id = following_id
        self.followee_type = followee_type
        self.status = status
        self.followed_at = followed_at

class MediaRow:
    def __init__(self, id, context_id, context_type, media_type, media_url, 
                 media_order, media_size, caption, uploaded_at):
        self.id = id
        self.context_id = context_id
        self.context_type = context_type
        self.media_type = media_type
        self.media_url = media_url
        self.media_order = media_order
        self.media_size = media_size
        self.caption = caption
        self.uploaded_at = uploaded_at

def get_user_by_id(id):
    if not isinstance(id, (int, str)):
        return None
    try:
        id = int(id)
    except (ValueError, TypeError):
        return None

    session = SessionLocal()
    try:
        result = session.execute(select(users).where(users.c.id == id)).fetchone()
        return UserRow(*result) if result else None
    finally:
        session.close()

def get_user_by_email(email):
    session = SessionLocal()
    try:
        result = session.execute(select(users).where(users.c.email == email)).fetchone()
        return UserRow(*result) if result else None
    finally:
        session.close()

def create_user(first_name, last_name, email, phone, password, role=None, address=None, 
                latitude=None, longitude=None, bio=None, gst_no=None,
                cover_photo_id=None, profile_photo_id=None):
    session = SessionLocal()
    try:
        # Validate required fields
        if not email or not password:
            raise ValueError("Email and password are required")

        # Check if email already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")

        result = session.execute(
            users.insert().returning(users.c.id).values(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                password=password,
                role=role,
                address=address,
                latitude=latitude,
                longitude=longitude,
                bio=bio,
                gst_no=gst_no,
                cover_photo_id=cover_photo_id,
                profile_photo_id=profile_photo_id,
                isactive=True,
                email_verified=False,
                phone_verified=False
            )
        )
        session.commit()
        return result.scalar()
    finally:
        session.close()

def create_rating(rated_user_id, rated_by_user_id, rating_value, title=None,
                review=None, rating_type=None, is_anonymous=False):
    session = SessionLocal()
    try:
        # Validate rating value
        if not 1 <= rating_value <= 5:
            raise ValueError("Rating value must be between 1 and 5")
            
        result = session.execute(
            ratings.insert().returning(ratings.c.id).values(
                rated_user_id=rated_user_id,
                rated_by_user_id=rated_by_user_id,
                rating_value=rating_value,
                title=title,
                review=review,
                rating_type=rating_type,
                is_anonymous=is_anonymous
            )
        )
        session.commit()
        return result.scalar()
    finally:
        session.close()

def get_ratings(user_id):
    session = SessionLocal()
    try:
        result = session.execute(
            select(ratings).where(ratings.c.rated_user_id == user_id)
        ).fetchall()
        return [RatingRow(*row) for row in result]
    finally:
        session.close()

def create_follower(follower_id, following_id, followee_type=None, status='active'):
    session = SessionLocal()
    try:
        result = session.execute(
            followers.insert().returning(followers.c.id).values(
                follower_id=follower_id,
                following_id=following_id,
                followee_type=followee_type,
                status=status
            )
        )
        session.commit()
        return result.scalar()
    finally:
        session.close()

def get_followers(user_id):
    session = SessionLocal()
    try:
        result = session.execute(
            select(followers).where(followers.c.following_id == user_id)
        ).fetchall()
        return [FollowerRow(*row) for row in result]
    finally:
        session.close()

def get_following(user_id):
    session = SessionLocal()
    try:
        result = session.execute(
            select(followers).where(followers.c.follower_id == user_id)
        ).fetchall()
        return [FollowerRow(*row) for row in result]
    finally:
        session.close()

def check_following_status(user_id, following_id):
    if not isinstance(user_id, (int, str)) or not isinstance(following_id, (int, str)):
        return None
    try:
        user_id = int(user_id)
        following_id = int(following_id)
    except (ValueError, TypeError):
        return None

    session = SessionLocal()
    try:
        # First verify both users exist
        user = session.execute(select(users).where(users.c.id == user_id)).fetchone()
        following = session.execute(select(users).where(users.c.id == following_id)).fetchone()
        
        if not user or not following:
            return None

        # Check following status
        result = session.execute(
            select(followers).where(
                and_(
                    followers.c.follower_id == user_id,
                    followers.c.following_id == following_id
                )
            )
        ).fetchone()
        
        return FollowerRow(*result) if result else None
    except Exception as e:
        print(f"Error checking following status: {str(e)}")
        return None
    finally:
        session.close()

def create_media(context_id, context_type, media_type, media_url, media_order=None, 
                media_size=None, caption=None):
    session = SessionLocal()
    try:
        result = session.execute(
            media.insert().returning(media.c.id).values(
                context_id=context_id,
                context_type=context_type,
                media_type=media_type,
                media_url=media_url,
                media_order=media_order,
                media_size=media_size,
                caption=caption
            )
        )
        session.commit()
        return result.scalar()
    finally:
        session.close()

def get_media_by_id(media_id):
    if not isinstance(media_id, (int, str)):
        return None
    try:
        media_id = int(media_id)
    except (ValueError, TypeError):
        return None

    session = SessionLocal()
    try:
        result = session.execute(select(media).where(media.c.id == media_id)).fetchone()
        return MediaRow(*result) if result else None
    finally:
        session.close()

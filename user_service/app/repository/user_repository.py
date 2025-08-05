from sqlalchemy.orm import sessionmaker
from user_service.app.utils.db_connection import get_db_engine
from sqlalchemy import select, and_
from user_service.app.entity.user_entity import users, ratings, followers

SessionLocal = sessionmaker(bind=get_db_engine())

class UserRow:
    def __init__(self, id, first_name, last_name, email, phone, profile_photo, role, address, 
                 latitude, longitude, bio, password, isactive, email_verified, phone_verified, 
                 last_login_at, created_at):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.profile_photo = profile_photo
        self.role = role
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.bio = bio
        self.password = password
        self.isactive = isactive
        self.email_verified = email_verified
        self.phone_verified = phone_verified
        self.last_login_at = last_login_at
        self.created_at = created_at

class RatingRow:
    def __init__(self, id, rated_user_id, rated_by_user_id, rating_value, title, review, 
                 rating_type, is_anonymous, created_at, updated_at):
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
                latitude=None, longitude=None, bio=None):
    session = SessionLocal()
    try:
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
                bio=bio
            )
        )
        session.commit()
        return result.scalar()
    finally:
        session.close()

def create_rating(rated_user_id, rated_by_user_id, rating_value, title=None, review=None, 
                 rating_type=None, is_anonymous=False):
    session = SessionLocal()
    try:
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

def get_user_ratings(user_id):
    session = SessionLocal()
    try:
        result = session.execute(
            select(ratings).where(ratings.c.rated_user_id == user_id)
        ).fetchall()
        return [RatingRow(*row) for row in result]
    finally:
        session.close()

def create_follower(follower_id, following_id, followee_type=None):
    session = SessionLocal()
    try:
        result = session.execute(
            followers.insert().returning(followers.c.id).values(
                follower_id=follower_id,
                following_id=following_id,
                followee_type=followee_type
            )
        )
        session.commit()
        return result.scalar()
    finally:
        session.close()

def get_user_followers(user_id):
    session = SessionLocal()
    try:
        result = session.execute(
            select(followers).where(followers.c.following_id == user_id)
        ).fetchall()
        return [FollowerRow(*row) for row in result]
    finally:
        session.close()

def get_user_following(user_id):
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

from posts_service.app.entity.post_entity import posts
from sqlalchemy.orm import sessionmaker
from posts_service.app.utils.db_connection import get_db_engine
from datetime import datetime

SessionLocal = sessionmaker(bind=get_db_engine())

def get_post_by_id(post_id):
    session = SessionLocal()
    query = posts.select().where(posts.c.post_id == post_id)
    post = session.execute(query).fetchone()
    session.close()
    return post

def create_post(user_id, title, content):
    session = SessionLocal()
    current_time = datetime.now()
    result = session.execute(posts.insert().returning(posts.c.post_id).values(
        user_id=user_id,
        title=title,
        content=content,
        created_at=current_time,
        updated_at=current_time
    ))
    session.commit()
    session.close()
    return result.scalar()

def get_user_posts(user_id):
    session = SessionLocal()
    query = posts.select().where(posts.c.user_id == user_id)
    user_posts = session.execute(query).fetchall()
    session.close()
    return user_posts 
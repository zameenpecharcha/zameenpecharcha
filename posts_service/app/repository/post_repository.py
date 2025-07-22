from ..entity.post_entity import Post, post_likes
from sqlalchemy.orm import sessionmaker, Session
from ..utils.db_connection import get_db_engine
from datetime import datetime
from typing import List, Optional

SessionLocal = sessionmaker(bind=get_db_engine())

class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        return self.db.query(Post).filter(Post.id == post_id).first()

    def create_post(self, user_id: int, title: str, content: str) -> Post:
        post = Post(
            user_id=user_id,
            title=title,
            content=content,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def get_user_posts(self, user_id: int) -> List[Post]:
        return self.db.query(Post).filter(Post.user_id == user_id).all()

    def get_post(self, post_id: int) -> Optional[Post]:
        return self.db.query(Post).filter(Post.id == post_id).first()

    def get_posts_by_user(self, user_id: int) -> List[Post]:
        return self.db.query(Post).filter(Post.user_id == user_id).all()

    def update_post(self, post_id: int, title: str, content: str) -> Optional[Post]:
        post = self.get_post(post_id)
        if post:
            post.title = title
            post.content = content
            post.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(post)
        return post

    def delete_post(self, post_id: int) -> bool:
        post = self.get_post(post_id)
        if post:
            self.db.delete(post)
            self.db.commit()
            return True
        return False

    def like_post(self, post_id: int, user_id: int) -> Optional[Post]:
        post = self.get_post(post_id)
        if post:
            # Check if user already liked the post
            existing_like = self.db.execute(
                post_likes.select().where(
                    post_likes.c.post_id == post_id,
                    post_likes.c.user_id == user_id
                )
            ).first()
            
            if not existing_like:
                self.db.execute(
                    post_likes.insert().values(
                        post_id=post_id,
                        user_id=user_id,
                        created_at=datetime.utcnow()
                    )
                )
                post.like_count += 1
                self.db.commit()
                self.db.refresh(post)
        return post

    def unlike_post(self, post_id: int, user_id: int) -> Optional[Post]:
        post = self.get_post(post_id)
        if post:
            # Check if user liked the post
            existing_like = self.db.execute(
                post_likes.select().where(
                    post_likes.c.post_id == post_id,
                    post_likes.c.user_id == user_id
                )
            ).first()
            
            if existing_like:
                self.db.execute(
                    post_likes.delete().where(
                        post_likes.c.post_id == post_id,
                        post_likes.c.user_id == user_id
                    )
                )
                post.like_count -= 1
                self.db.commit()
                self.db.refresh(post)
        return post

    def increment_comment_count(self, post_id: int) -> Optional[Post]:
        post = self.get_post(post_id)
        if post:
            post.comment_count += 1
            self.db.commit()
            self.db.refresh(post)
        return post

    def decrement_comment_count(self, post_id: int) -> Optional[Post]:
        post = self.get_post(post_id)
        if post and post.comment_count > 0:
            post.comment_count -= 1
            self.db.commit()
            self.db.refresh(post)
        return post 
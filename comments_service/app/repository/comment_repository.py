from sqlalchemy.orm import Session
from ..entity.comment_entity import Comment, comment_likes
from typing import List, Optional

class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_comment(self, comment: Comment) -> Comment:
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_comment(self, comment_id: int) -> Optional[Comment]:
        return self.db.query(Comment).filter(Comment.id == comment_id).first()

    def get_comments_by_post(self, post_id: int) -> List[Comment]:
        return self.db.query(Comment).filter(Comment.post_id == post_id).all()

    def get_replies(self, parent_comment_id: int) -> List[Comment]:
        return self.db.query(Comment).filter(Comment.parent_comment_id == parent_comment_id).all()

    def update_comment(self, comment_id: int, content: str) -> Optional[Comment]:
        comment = self.get_comment(comment_id)
        if comment:
            comment.content = content
            self.db.commit()
            self.db.refresh(comment)
        return comment

    def delete_comment(self, comment_id: int) -> bool:
        comment = self.get_comment(comment_id)
        if comment:
            self.db.delete(comment)
            self.db.commit()
            return True
        return False

    def like_comment(self, comment_id: int, user_id: int) -> Optional[Comment]:
        comment = self.get_comment(comment_id)
        if comment:
            # Check if user already liked the comment
            existing_like = self.db.execute(
                comment_likes.select().where(
                    comment_likes.c.comment_id == comment_id,
                    comment_likes.c.user_id == user_id
                )
            ).first()
            
            if not existing_like:
                self.db.execute(
                    comment_likes.insert().values(
                        comment_id=comment_id,
                        user_id=user_id
                    )
                )
                comment.like_count += 1
                self.db.commit()
                self.db.refresh(comment)
        return comment

    def unlike_comment(self, comment_id: int, user_id: int) -> Optional[Comment]:
        comment = self.get_comment(comment_id)
        if comment:
            # Check if user liked the comment
            existing_like = self.db.execute(
                comment_likes.select().where(
                    comment_likes.c.comment_id == comment_id,
                    comment_likes.c.user_id == user_id
                )
            ).first()
            
            if existing_like:
                self.db.execute(
                    comment_likes.delete().where(
                        comment_likes.c.comment_id == comment_id,
                        comment_likes.c.user_id == user_id
                    )
                )
                comment.like_count -= 1
                self.db.commit()
                self.db.refresh(comment)
        return comment 
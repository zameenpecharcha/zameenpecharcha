from sqlalchemy.orm import Session
from ..repository.comment_repository import CommentRepository
from ..entity.comment_entity import Comment
from typing import List, Optional
from datetime import datetime

class CommentService:
    def __init__(self, db: Session):
        self.repository = CommentRepository(db)

    def create_comment(self, post_id: int, user_id: int, content: str, parent_comment_id: Optional[int] = None) -> Comment:
        comment = Comment(
            post_id=post_id,
            user_id=user_id,
            content=content,
            parent_comment_id=parent_comment_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            like_count=0
        )
        return self.repository.create_comment(comment)

    def get_comment(self, comment_id: int) -> Optional[Comment]:
        return self.repository.get_comment(comment_id)

    def get_comments_by_post(self, post_id: int) -> List[Comment]:
        return self.repository.get_comments_by_post(post_id)

    def get_replies(self, parent_comment_id: int) -> List[Comment]:
        return self.repository.get_replies(parent_comment_id)

    def update_comment(self, comment_id: int, content: str) -> Optional[Comment]:
        return self.repository.update_comment(comment_id, content)

    def delete_comment(self, comment_id: int) -> bool:
        return self.repository.delete_comment(comment_id)

    def like_comment(self, comment_id: int, user_id: int) -> Optional[Comment]:
        return self.repository.like_comment(comment_id, user_id)

    def unlike_comment(self, comment_id: int, user_id: int) -> Optional[Comment]:
        return self.repository.unlike_comment(comment_id, user_id) 
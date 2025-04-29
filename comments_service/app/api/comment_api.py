from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..service.comment_service import CommentService
from ..entity.comment_entity import Comment
from ..utils.db_connection import get_db
from pydantic import BaseModel

router = APIRouter()

class CommentCreate(BaseModel):
    post_id: int
    content: str
    parent_comment_id: int = None

class CommentUpdate(BaseModel):
    content: str

@router.post("/", response_model=Comment)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    service = CommentService(db)
    return service.create_comment(
        post_id=comment.post_id,
        user_id=1,  # TODO: Get from auth token
        content=comment.content,
        parent_comment_id=comment.parent_comment_id
    )

@router.get("/{comment_id}", response_model=Comment)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    service = CommentService(db)
    comment = service.get_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.get("/post/{post_id}", response_model=List[Comment])
def get_comments_by_post(post_id: int, db: Session = Depends(get_db)):
    service = CommentService(db)
    return service.get_comments_by_post(post_id)

@router.get("/{comment_id}/replies", response_model=List[Comment])
def get_replies(comment_id: int, db: Session = Depends(get_db)):
    service = CommentService(db)
    return service.get_replies(comment_id)

@router.put("/{comment_id}", response_model=Comment)
def update_comment(comment_id: int, comment: CommentUpdate, db: Session = Depends(get_db)):
    service = CommentService(db)
    updated_comment = service.update_comment(comment_id, comment.content)
    if not updated_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return updated_comment

@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    service = CommentService(db)
    success = service.delete_comment(comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Comment deleted successfully"} 
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from ..entity.post_entity import Post, PostMedia, PostLike, CommentLike
from ..models.comment import CommentReference
from ..models.user import UserReference

class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    # Post Operations
    def create_post(self, user_id: int, title: str, content: str, visibility: str = None,
                   property_type: str = None, location: str = None, map_location: str = None,
                   price: float = None, status: str = 'active') -> Post:
        try:
            post = Post(
                user_id=user_id,
                title=title,
                content=content,
                visibility=visibility,
                property_type=property_type,
                location=location,
                map_location=map_location,
                price=price,
                status=status,
                created_at=datetime.utcnow()
            )
            self.db.add(post)
            self.db.commit()
            self.db.refresh(post)
            return post
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error while creating post: {str(e)}")

    def get_post(self, post_id: int) -> Optional[Post]:
        try:
            return self.db.query(Post).filter(Post.id == post_id).first()
        except SQLAlchemyError as e:
            raise Exception(f"Database error while fetching post: {str(e)}")

    def update_post(self, post_id: int, title: str = None, content: str = None,
                   visibility: str = None, property_type: str = None,
                   location: str = None, map_location: str = None,
                   price: float = None, status: str = None) -> Optional[Post]:
        try:
            post = self.get_post(post_id)
            if post:
                if title is not None:
                    post.title = title
                if content is not None:
                    post.content = content
                if visibility is not None:
                    post.visibility = visibility
                if property_type is not None:
                    post.property_type = property_type
                if location is not None:
                    post.location = location
                if map_location is not None:
                    post.map_location = map_location
                if price is not None:
                    post.price = price
                if status is not None:
                    post.status = status
                self.db.commit()
                self.db.refresh(post)
            return post
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error while updating post: {str(e)}")

    def delete_post(self, post_id: int) -> bool:
        try:
            post = self.get_post(post_id)
            if post:
                self.db.delete(post)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error while deleting post: {str(e)}")

    def get_posts_by_user(self, user_id: int, page: int = 1, limit: int = 10) -> Tuple[List[Post], int]:
        try:
            query = self.db.query(Post).filter(Post.user_id == user_id)
            total = query.count()
            posts = query.order_by(desc(Post.created_at)).offset((page - 1) * limit).limit(limit).all()
            return posts, total
        except SQLAlchemyError as e:
            raise Exception(f"Database error while fetching user posts: {str(e)}")

    def search_posts(self, property_type: str = None, location: str = None,
                    min_price: float = None, max_price: float = None,
                    status: str = None, page: int = 1, limit: int = 10) -> Tuple[List[Post], int]:
        try:
            print("Starting search_posts in repository")
            query = self.db.query(Post)
            
            # Only apply filters if they are explicitly provided
            if property_type and property_type.strip():
                print(f"Filtering by property_type: {property_type}")
                query = query.filter(Post.property_type == property_type)
            if location and location.strip():
                print(f"Filtering by location: {location}")
                query = query.filter(Post.location.ilike(f"%{location}%"))
            if min_price is not None and min_price > 0:
                print(f"Filtering by min_price: {min_price}")
                query = query.filter(Post.price >= min_price)
            if max_price is not None and max_price > 0:
                print(f"Filtering by max_price: {max_price}")
                query = query.filter(Post.price <= max_price)
            if status and status.strip():
                print(f"Filtering by status: {status}")
                query = query.filter(Post.status == status)
            
            total = query.count()
            print(f"Total posts before pagination: {total}")
            
            posts = query.order_by(desc(Post.created_at)).offset((page - 1) * limit).limit(limit).all()
            print(f"Retrieved {len(posts)} posts after pagination")
            
            return posts, total
        except SQLAlchemyError as e:
            print(f"Database error in search_posts: {str(e)}")
            raise Exception(f"Database error while searching posts: {str(e)}")
        except Exception as e:
            print(f"Unexpected error in search_posts: {str(e)}")
            raise e

    # Media Operations
    def add_post_media(self, post_id: int, media_type: str, media_url: str,
                      media_order: int, media_size: int = 0, caption: str = None) -> PostMedia:
        try:
            media = PostMedia(
                post_id=post_id,
                media_type=media_type,
                media_url=media_url,
                media_order=media_order,
                media_size=media_size,
                caption=caption,
                uploaded_at=datetime.utcnow()
            )
            self.db.add(media)
            self.db.commit()
            self.db.refresh(media)
            return media
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error while adding media: {str(e)}")

    def delete_post_media(self, media_id: int) -> bool:
        media = self.db.query(PostMedia).filter(PostMedia.id == media_id).first()
        if media:
            self.db.delete(media)
            self.db.commit()
            return True
        return False

    # Like Operations
    def like_post(self, post_id: int, user_id: int, reaction_type: str = 'like') -> Optional[Post]:
        try:
            # First check if post exists
            post = self.get_post(post_id)
            if not post:
                raise Exception(f"Post with ID {post_id} not found")

            # Check if user has already liked the post
            existing_like = self.db.query(PostLike).filter(
                PostLike.post_id == post_id,
                PostLike.user_id == user_id
            ).first()
            
            if not existing_like:
                try:
                    like = PostLike(
                        post_id=post_id,  # Make sure we're using the correct post_id
                        user_id=user_id,
                        reaction_type=reaction_type,
                        liked_at=datetime.utcnow()
                    )
                    self.db.add(like)
                    self.db.commit()
                except SQLAlchemyError as e:
                    self.db.rollback()
                    raise Exception(f"Database error while adding like: {str(e)}")
            
            # Get fresh post data with updated like count
            try:
                self.db.refresh(post)
                return post
            except SQLAlchemyError as e:
                self.db.rollback()
                raise Exception(f"Database error while refreshing post: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise e

    def unlike_post(self, post_id: int, user_id: int) -> Optional[Post]:
        try:
            # First check if post exists
            post = self.get_post(post_id)
            if not post:
                raise Exception(f"Post with ID {post_id} not found")

            # Check if user has liked the post
            like = self.db.query(PostLike).filter(
                PostLike.post_id == post_id,
                PostLike.user_id == user_id
            ).first()
            
            if like:
                try:
                    self.db.delete(like)
                    self.db.commit()
                except SQLAlchemyError as e:
                    self.db.rollback()
                    raise Exception(f"Database error while removing like: {str(e)}")
            
            # Get fresh post data with updated like count
            try:
                self.db.refresh(post)
                return post
            except SQLAlchemyError as e:
                self.db.rollback()
                raise Exception(f"Database error while refreshing post: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise e

    # Comment Operations
    def create_comment(self, post_id: int, user_id: int, comment_text: str,
                      parent_comment_id: int = None) -> CommentReference:
        try:
            # For replies (parent_comment_id > 0), verify parent comment exists
            if parent_comment_id and parent_comment_id > 0:
                parent_comment = self.get_comment(parent_comment_id)
                if not parent_comment:
                    raise Exception(f"Parent comment with ID {parent_comment_id} not found")
                # Verify parent comment belongs to the same post
                if parent_comment.post_id != post_id:
                    raise Exception("Parent comment does not belong to the specified post")
            else:
                # For new comments (parent_comment_id = 0 or None), set to None
                parent_comment_id = None

            # Create the comment
            comment = CommentReference(
                post_id=post_id,
                user_id=user_id,
                comment=comment_text,
                parent_comment_id=parent_comment_id,  # Will be NULL for new comments, actual ID for replies
                added_at=datetime.utcnow(),
                commented_at=datetime.utcnow(),
                status='active'
            )
            self.db.add(comment)
            self.db.commit()
            self.db.refresh(comment)
            return comment
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error while creating comment: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise e

    def get_comment(self, comment_id: int) -> Optional[CommentReference]:
        return self.db.query(CommentReference).filter(CommentReference.id == comment_id).first()

    def get_comment_replies(self, comment_id: int, page: int = 1, limit: int = 10) -> Tuple[List[CommentReference], int]:
        query = self.db.query(CommentReference).filter(
            CommentReference.parent_comment_id == comment_id
        )
        total = query.count()
        replies = query.order_by(desc(CommentReference.commented_at)).offset((page - 1) * limit).limit(limit).all()
        return replies, total

    def update_comment(self, comment_id: int, comment_text: str = None,
                      status: str = None) -> Optional[CommentReference]:
        comment = self.get_comment(comment_id)
        if comment:
            if comment_text is not None:
                comment.comment = comment_text
                comment.commented_at = datetime.utcnow()
            if status is not None:
                comment.status = status
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

    def get_comment_thread(self, comment_id: int) -> List[CommentReference]:
        """Get a comment and all its nested replies in a flat list"""
        def get_replies(comment):
            result = [comment]
            for reply in comment.replies:
                result.extend(get_replies(reply))
            return result

        comment = self.get_comment(comment_id)
        if not comment:
            return []
        
        return get_replies(comment)

    def get_comments(self, post_id: int, page: int = 1, limit: int = 10) -> Tuple[List[CommentReference], int]:
        # Get only top-level comments (no parent)
        query = self.db.query(CommentReference).filter(
            CommentReference.post_id == post_id,
            CommentReference.parent_comment_id.is_(None)
        ).order_by(desc(CommentReference.commented_at))

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        offset = (page - 1) * limit
        comments = query.offset(offset).limit(limit).all()

        return comments, total

    def like_comment(self, comment_id: int, user_id: int, reaction_type: str = 'like') -> Optional[CommentReference]:
        try:
            # First check if comment exists
            comment = self.get_comment(comment_id)
            if not comment:
                raise Exception(f"Comment with ID {comment_id} not found")

            # Check if user has already liked the comment
            existing_like = self.db.query(CommentLike).filter(
                CommentLike.comment_id == comment_id,
                CommentLike.user_id == user_id
            ).first()
            
            if not existing_like:
                try:
                    like = CommentLike(
                        comment_id=comment_id,
                        user_id=user_id,
                        reaction_type=reaction_type,
                        liked_at=datetime.utcnow()
                    )
                    self.db.add(like)
                    self.db.commit()
                except SQLAlchemyError as e:
                    self.db.rollback()
                    raise Exception(f"Database error while adding like: {str(e)}")
            
            # Get fresh comment data with updated like count
            try:
                self.db.refresh(comment)
                return comment
            except SQLAlchemyError as e:
                self.db.rollback()
                raise Exception(f"Database error while refreshing comment: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise e

    def unlike_comment(self, comment_id: int, user_id: int) -> Optional[CommentReference]:
        try:
            # First check if comment exists
            comment = self.get_comment(comment_id)
            if not comment:
                raise Exception(f"Comment with ID {comment_id} not found")

            # Check if user has liked the comment
            like = self.db.query(CommentLike).filter(
                CommentLike.comment_id == comment_id,
                CommentLike.user_id == user_id
            ).first()
            
            if like:
                try:
                    self.db.delete(like)
                    self.db.commit()
                except SQLAlchemyError as e:
                    self.db.rollback()
                    raise Exception(f"Database error while removing like: {str(e)}")
            
            # Get fresh comment data with updated like count
            try:
                self.db.refresh(comment)
                return comment
            except SQLAlchemyError as e:
                self.db.rollback()
                raise Exception(f"Database error while refreshing comment: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise e

    # Helper Methods
    def get_post_like_count(self, post_id: int) -> int:
        return self.db.query(PostLike).filter(PostLike.post_id == post_id).count()

    def get_comment_like_count(self, comment_id: int) -> int:
        return self.db.query(CommentLike).filter(CommentLike.comment_id == comment_id).count()

    def get_post_comment_count(self, post_id: int) -> int:
        # Count only top-level comments
        return self.db.query(CommentReference).filter(
            CommentReference.post_id == post_id,
            CommentReference.parent_comment_id.is_(None)
        ).count() 
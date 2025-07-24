from sqlalchemy.orm import Session
from ..repository.comment_repository import CommentRepository
from ..entity.comment_entity import Comment
from typing import List, Optional
from datetime import datetime
import grpc
from concurrent import futures
import logging
from ..utils.db_connection import engine, SessionLocal, Base
from ..proto_files import comments_pb2, comments_pb2_grpc
import os
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

class CommentService:
    def __init__(self, db: Session):
        self.repository = CommentRepository(db)
        # Create channels to user and post services
        self.user_channel = grpc.insecure_channel('localhost:50051')
        self.post_channel = grpc.insecure_channel('localhost:50052')
        
        # Import and create stubs
        from user_service.app.proto_files.user_pb2_grpc import UserServiceStub
        from posts_service.app.proto_files.post_pb2_grpc import PostsServiceStub
        self.user_stub = UserServiceStub(self.user_channel)
        self.post_stub = PostsServiceStub(self.post_channel)

    def validate_user(self, user_id: str) -> bool:
        try:
            from user_service.app.proto_files.user_pb2 import UserRequest
            response = self.user_stub.GetUser(UserRequest(id=int(user_id)))
            return True
        except Exception as e:
            logger.error(f"Error validating user {user_id}: {str(e)}")
            return False

    def validate_post(self, post_id: str) -> bool:
        try:
            from posts_service.app.proto_files.post_pb2 import PostRequest
            response = self.post_stub.GetPost(PostRequest(post_id=post_id))
            return True
        except Exception as e:
            logger.error(f"Error validating post {post_id}: {str(e)}")
            return False

    def create_comment(self, post_id: str, user_id: str, content: str, parent_comment_id: Optional[str] = None) -> Comment:
        # Validate user exists
        if not self.validate_user(user_id):
            raise ValueError(f"User {user_id} not found")

        # Validate post exists
        if not self.validate_post(post_id):
            raise ValueError(f"Post {post_id} not found")

        # If parent_comment_id is provided, verify it exists
        if parent_comment_id:
            parent_comment = self.repository.get_comment(uuid.UUID(parent_comment_id))
            if not parent_comment:
                raise ValueError(f"Parent comment with ID {parent_comment_id} does not exist")

        now = datetime.utcnow()
        comment = Comment(
            post_id=uuid.UUID(post_id),
            user_id=uuid.UUID(user_id),
            content=content,
            parent_comment_id=uuid.UUID(parent_comment_id) if parent_comment_id else None,
            created_at=now,
            updated_at=now,
            like_count=0
        )
        return self.repository.create_comment(comment)

    def get_comment(self, comment_id: str) -> Optional[Comment]:
        return self.repository.get_comment(uuid.UUID(comment_id))

    def get_comments_by_post(self, post_id: str) -> List[Comment]:
        # Validate post exists before getting comments
        if not self.validate_post(post_id):
            raise ValueError(f"Post {post_id} not found")
        return self.repository.get_comments_by_post(uuid.UUID(post_id))

    def get_replies(self, parent_comment_id: str) -> List[Comment]:
        # Validate parent comment exists
        parent_comment = self.repository.get_comment(uuid.UUID(parent_comment_id))
        if not parent_comment:
            raise ValueError(f"Parent comment {parent_comment_id} not found")
        return self.repository.get_replies(uuid.UUID(parent_comment_id))

    def update_comment(self, comment_id: str, content: str) -> Optional[Comment]:
        return self.repository.update_comment(uuid.UUID(comment_id), content)

    def delete_comment(self, comment_id: str) -> bool:
        return self.repository.delete_comment(uuid.UUID(comment_id))

    def like_comment(self, comment_id: str, user_id: str) -> Optional[Comment]:
        # Validate user exists before liking
        if not self.validate_user(user_id):
            raise ValueError(f"User {user_id} not found")
        return self.repository.like_comment(uuid.UUID(comment_id), uuid.UUID(user_id))

    def unlike_comment(self, comment_id: str, user_id: str) -> Optional[Comment]:
        # Validate user exists before unliking
        if not self.validate_user(user_id):
            raise ValueError(f"User {user_id} not found")
        return self.repository.unlike_comment(uuid.UUID(comment_id), uuid.UUID(user_id))

class CommentsServicer(comments_pb2_grpc.CommentsServiceServicer):
    def __init__(self):
        pass  # Don't create db session in constructor

    def get_db(self):
        db = SessionLocal()
        try:
            return db
        except:
            db.close()
            raise

    def CreateComment(self, request, context):
        db = None
        try:
            db = self.get_db()
            service = CommentService(db)
            
            # For the first comment, don't include parent_comment_id
            parent_comment_id = request.parent_comment_id if request.parent_comment_id and request.parent_comment_id.strip() else None
            
            comment = service.create_comment(
                post_id=request.post_id,
                user_id=request.user_id,
                content=request.content,
                parent_comment_id=parent_comment_id
            )
            return comments_pb2.CommentResponse(
                success=True,
                message="Comment created successfully",
                comment=comments_pb2.Comment(
                    comment_id=str(comment.id),
                    post_id=str(comment.post_id),
                    user_id=str(comment.user_id),
                    content=comment.content,
                    parent_comment_id=str(comment.parent_comment_id) if comment.parent_comment_id else "",
                    created_at=int(comment.created_at.timestamp()),
                    updated_at=int(comment.updated_at.timestamp()),
                    like_count=comment.like_count
                )
            )
        except ValueError as e:
            logger.error(f"Error creating comment - validation error: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))
        except Exception as e:
            logger.error(f"Error creating comment: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))
        finally:
            if db:
                db.close()

    def GetComment(self, request, context):
        db = None
        try:
            db = self.get_db()
            service = CommentService(db)
            comment = service.get_comment(request.comment_id)
            if not comment:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return comments_pb2.CommentResponse(success=False, message="Comment not found")
            
            return comments_pb2.CommentResponse(
                success=True,
                message="Comment retrieved successfully",
                comment=comments_pb2.Comment(
                    comment_id=str(comment.id),
                    post_id=str(comment.post_id),
                    user_id=str(comment.user_id),
                    content=comment.content,
                    parent_comment_id=str(comment.parent_comment_id) if comment.parent_comment_id else "",
                    created_at=int(comment.created_at.timestamp()),
                    updated_at=int(comment.updated_at.timestamp()),
                    like_count=comment.like_count
                )
            )
        except ValueError as e:
            logger.error(f"Error getting comment - invalid UUID: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid UUID format: {str(e)}")
            return comments_pb2.CommentResponse(success=False, message=str(e))
        except Exception as e:
            logger.error(f"Error getting comment: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))
        finally:
            if db:
                db.close()

    def UpdateComment(self, request, context):
        db = None
        try:
            db = self.get_db()
            service = CommentService(db)
            
            # First check if the comment exists
            existing_comment = service.get_comment(request.comment_id)
            if not existing_comment:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return comments_pb2.CommentResponse(
                    success=False,
                    message=f"Comment with ID {request.comment_id} not found"
                )
            
            # Update the comment
            updated_comment = service.update_comment(
                comment_id=request.comment_id,
                content=request.content
            )
            
            return comments_pb2.CommentResponse(
                success=True,
                message="Comment updated successfully",
                comment=comments_pb2.Comment(
                    comment_id=str(updated_comment.id),
                    post_id=str(updated_comment.post_id),
                    user_id=str(updated_comment.user_id),
                    content=updated_comment.content,
                    parent_comment_id=str(updated_comment.parent_comment_id) if updated_comment.parent_comment_id else "",
                    created_at=int(updated_comment.created_at.timestamp()),
                    updated_at=int(updated_comment.updated_at.timestamp()),
                    like_count=updated_comment.like_count
                )
            )
        except ValueError as e:
            logger.error(f"Error updating comment - validation error: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))
        except Exception as e:
            logger.error(f"Error updating comment: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))
        finally:
            if db:
                db.close()

    def DeleteComment(self, request, context):
        db = None
        try:
            db = self.get_db()
            service = CommentService(db)
            
            # First check if the comment exists
            existing_comment = service.get_comment(request.comment_id)
            if not existing_comment:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return comments_pb2.CommentResponse(
                    success=False,
                    message=f"Comment with ID {request.comment_id} not found"
                )
            
            # Delete the comment
            success = service.delete_comment(request.comment_id)
            
            if success:
                return comments_pb2.CommentResponse(
                    success=True,
                    message="Comment deleted successfully"
                )
            else:
                context.set_code(grpc.StatusCode.INTERNAL)
                return comments_pb2.CommentResponse(
                    success=False,
                    message="Failed to delete comment"
                )
                
        except ValueError as e:
            logger.error(f"Error deleting comment - validation error: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))
        except Exception as e:
            logger.error(f"Error deleting comment: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))
        finally:
            if db:
                db.close()

    def GetCommentsByPost(self, request, context):
        db = None
        try:
            db = self.get_db()
            service = CommentService(db)
            
            # Validate UUID format
            try:
                logger.info(f"Attempting to validate post_id UUID: {request.post_id}")
                # Remove any whitespace and ensure proper format
                post_id = request.post_id.strip()
                if not post_id:
                    raise ValueError("post_id cannot be empty")
                
                # Try to parse the UUID
                try:
                    post_uuid = uuid.UUID(post_id)
                except ValueError:
                    # If it fails, try to add hyphens if they're missing
                    if len(post_id) == 32:
                        post_id = f"{post_id[:8]}-{post_id[8:12]}-{post_id[12:16]}-{post_id[16:20]}-{post_id[20:]}"
                        post_uuid = uuid.UUID(post_id)
                    else:
                        raise
                
                logger.info(f"Successfully validated post_id UUID: {post_uuid}")
            except ValueError as e:
                logger.error(f"Failed to validate post_id UUID: {request.post_id}, error: {str(e)}")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Invalid post_id format. Expected a valid UUID.")
                return comments_pb2.CommentListResponse(
                    success=False,
                    message="Invalid post_id format. Expected a valid UUID."
                )
            
            # Get all comments for the post using the validated UUID string
            comments = service.get_comments_by_post(str(post_uuid))
            
            # Convert comments to proto message format
            comment_list = comments_pb2.CommentList(
                comments=[
                    comments_pb2.Comment(
                        comment_id=str(comment.id),
                        post_id=str(comment.post_id),
                        user_id=str(comment.user_id),
                        content=comment.content,
                        parent_comment_id=str(comment.parent_comment_id) if comment.parent_comment_id else "",
                        created_at=int(comment.created_at.timestamp()),
                        updated_at=int(comment.updated_at.timestamp()),
                        like_count=comment.like_count
                    ) for comment in comments
                ]
            )
            
            return comments_pb2.CommentListResponse(
                success=True,
                message="Comments retrieved successfully",
                comments=comment_list
            )
                
        except ValueError as e:
            logger.error(f"Error getting comments - validation error: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return comments_pb2.CommentListResponse(success=False, message=str(e))
        except Exception as e:
            logger.error(f"Error getting comments: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.CommentListResponse(success=False, message=str(e))
        finally:
            if db:
                db.close()

    def LikeComment(self, request, context):
        db = None
        try:
            db = self.get_db()
            service = CommentService(db)
            
            # Validate UUIDs
            try:
                comment_uuid = uuid.UUID(request.comment_id)
                user_uuid = uuid.UUID(request.user_id)
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Invalid UUID format")
                return comments_pb2.CommentResponse(
                    success=False,
                    message="Invalid UUID format"
                )
            
            # Like the comment
            comment = service.like_comment(request.comment_id, request.user_id)
            if not comment:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return comments_pb2.CommentResponse(
                    success=False,
                    message="Comment not found"
                )
            
            return comments_pb2.CommentResponse(
                success=True,
                message="Comment liked successfully",
                comment=comments_pb2.Comment(
                    comment_id=str(comment.id),
                    post_id=str(comment.post_id),
                    user_id=str(comment.user_id),
                    content=comment.content,
                    parent_comment_id=str(comment.parent_comment_id) if comment.parent_comment_id else "",
                    created_at=int(comment.created_at.timestamp()),
                    updated_at=int(comment.updated_at.timestamp()),
                    like_count=comment.like_count
                )
            )
                
        except ValueError as e:
            logger.error(f"Error liking comment - validation error: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))
        except Exception as e:
            logger.error(f"Error liking comment: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))
        finally:
            if db:
                db.close()

    def UnlikeComment(self, request, context):
        db = None
        try:
            db = self.get_db()
            service = CommentService(db)
            
            # Validate UUIDs
            try:
                comment_uuid = uuid.UUID(request.comment_id)
                user_uuid = uuid.UUID(request.user_id)
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Invalid UUID format")
                return comments_pb2.CommentResponse(
                    success=False,
                    message="Invalid UUID format"
                )
            
            # Unlike the comment
            comment = service.unlike_comment(request.comment_id, request.user_id)
            if not comment:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return comments_pb2.CommentResponse(
                    success=False,
                    message="Comment not found"
                )
            
            return comments_pb2.CommentResponse(
                success=True,
                message="Comment unliked successfully",
                comment=comments_pb2.Comment(
                    comment_id=str(comment.id),
                    post_id=str(comment.post_id),
                    user_id=str(comment.user_id),
                    content=comment.content,
                    parent_comment_id=str(comment.parent_comment_id) if comment.parent_comment_id else "",
                    created_at=int(comment.created_at.timestamp()),
                    updated_at=int(comment.updated_at.timestamp()),
                    like_count=comment.like_count
                )
            )
                
        except ValueError as e:
            logger.error(f"Error unliking comment - validation error: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))
        except Exception as e:
            logger.error(f"Error unliking comment: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))
        finally:
            if db:
                db.close()

def serve():
    # Create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    comments_pb2_grpc.add_CommentsServiceServicer_to_server(CommentsServicer(), server)
    port = 50058  # Using a different port
    server.add_insecure_port(f'[::]:{port}')
    logger.info(f"Starting comments service on port {port}...")
    server.start()
    logger.info("Comments service is running...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve() 
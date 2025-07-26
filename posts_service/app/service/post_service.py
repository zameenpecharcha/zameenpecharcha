import grpc
from concurrent import futures
from datetime import datetime
import os
from dotenv import load_dotenv
from ..proto_files import post_pb2, post_pb2_grpc
from ..repository.post_repository import PostRepository
from ..utils.db_connection import get_db_engine
from sqlalchemy.orm import sessionmaker
from ..models.user import UserReference
from ..models.comment import CommentReference

# Load environment variables
load_dotenv()

# Create database session
SessionLocal = sessionmaker(bind=get_db_engine())

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PostsService(post_pb2_grpc.PostsServiceServicer):
    def __init__(self):
        self.db = next(get_db())
        self.repository = PostRepository(self.db)

    def _convert_timestamp(self, dt):
        return int(dt.timestamp()) if dt else 0

    def _convert_to_proto_post(self, post):
        if not post:
            return None

        return post_pb2.Post(
            id=post.id,
            user_id=post.user_id,
            title=post.title,
            content=post.content,
            visibility=post.visibility or "",
            property_type=post.property_type or "",
            location=post.location or "",
            map_location=post.map_location or "",
            price=float(post.price) if post.price else 0.0,
            status=post.status or "",
            created_at=self._convert_timestamp(post.created_at),
            media=[self._convert_to_proto_media(m) for m in post.media],
            comments=[self._convert_to_proto_comment(c) for c in post.comments],
            like_count=len(post.likes),
            comment_count=len(post.comments)
        )

    def _convert_to_proto_media(self, media):
        return post_pb2.PostMedia(
            id=media.id,
            post_id=media.post_id,
            media_type=media.media_type,
            media_url=media.media_url,
            media_order=media.media_order,
            media_size=media.media_size,
            caption=media.caption or "",
            uploaded_at=self._convert_timestamp(media.uploaded_at)
        )

    def _convert_to_proto_comment(self, comment):
        return post_pb2.Comment(
            id=comment.id,
            post_id=comment.post_id,
            parent_comment_id=comment.parent_comment_id or 0,
            comment=comment.comment,
            user_id=comment.user_id,
            status=comment.status,
            added_at=self._convert_timestamp(comment.added_at),
            commented_at=self._convert_timestamp(comment.commented_at),
            replies=[self._convert_to_proto_comment(r) for r in comment.replies],
            like_count=len(comment.likes)
        )

    def CreatePost(self, request, context):
        try:
            # First check if user exists
            user = self.db.query(UserReference).filter(UserReference.id == request.user_id).first()
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with id {request.user_id} not found")
                return post_pb2.PostResponse(
                    success=False,
                    message=f"User with id {request.user_id} not found"
                )

            post = self.repository.create_post(
                user_id=request.user_id,
                title=request.title,
                content=request.content,
                visibility=request.visibility,
                property_type=request.property_type,
                location=request.location,
                map_location=request.map_location,
                price=request.price,
                status=request.status
            )

            # Handle media uploads if any
            for media in request.media:
                # Here you would implement media file handling
                # For now, we'll assume media_url is provided
                self.repository.add_post_media(
                    post_id=post.id,
                    media_type=media.media_type,
                    media_url="placeholder_url",  # This would be replaced with actual upload logic
                    media_order=media.media_order,
                    media_size=0,  # This would be actual file size
                    caption=media.caption
                )

            return post_pb2.PostResponse(
                success=True,
                message="Post created successfully",
                post=self._convert_to_proto_post(post)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.PostResponse(
                success=False,
                message=f"Failed to create post: {str(e)}"
            )

    def GetPost(self, request, context):
        try:
            post = self.repository.get_post(request.post_id)
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return post_pb2.PostResponse(
                    success=False,
                    message="Post not found"
                )

            return post_pb2.PostResponse(
                success=True,
                message="Post retrieved successfully",
                post=self._convert_to_proto_post(post)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.PostResponse(
                success=False,
                message=f"Failed to get post: {str(e)}"
            )

    def UpdatePost(self, request, context):
        try:
            post = self.repository.update_post(
                post_id=request.post_id,
                title=request.title,
                content=request.content,
                visibility=request.visibility,
                property_type=request.property_type,
                location=request.location,
                map_location=request.map_location,
                price=request.price,
                status=request.status
            )
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return post_pb2.PostResponse(
                    success=False,
                    message="Post not found"
                )

            return post_pb2.PostResponse(
                success=True,
                message="Post updated successfully",
                post=self._convert_to_proto_post(post)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.PostResponse(
                success=False,
                message=f"Failed to update post: {str(e)}"
            )

    def DeletePost(self, request, context):
        try:
            success = self.repository.delete_post(request.post_id)
            if not success:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return post_pb2.GenericResponse(
                    success=False,
                    message="Post not found"
                )

            return post_pb2.GenericResponse(
                success=True,
                message="Post deleted successfully"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.GenericResponse(
                success=False,
                message=f"Failed to delete post: {str(e)}"
            )

    def GetPostsByUser(self, request, context):
        try:
            posts, total = self.repository.get_posts_by_user(
                user_id=request.user_id,
                page=request.page,
                limit=request.limit
            )

            return post_pb2.PostListResponse(
                success=True,
                message="Posts retrieved successfully",
                posts=[self._convert_to_proto_post(p) for p in posts],
                total_count=total,
                page=request.page,
                total_pages=(total + request.limit - 1) // request.limit
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.PostListResponse(
                success=False,
                message=f"Failed to get posts: {str(e)}"
            )

    def SearchPosts(self, request, context):
        try:
            posts, total = self.repository.search_posts(
                property_type=request.property_type,
                location=request.location,
                min_price=request.min_price,
                max_price=request.max_price,
                status=request.status,
                page=request.page,
                limit=request.limit
            )

            return post_pb2.PostListResponse(
                success=True,
                message="Posts retrieved successfully",
                posts=[self._convert_to_proto_post(p) for p in posts],
                total_count=total,
                page=request.page,
                total_pages=(total + request.limit - 1) // request.limit
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.PostListResponse(
                success=False,
                message=f"Failed to search posts: {str(e)}"
            )

    def AddPostMedia(self, request, context):
        try:
            post = self.repository.get_post(request.post_id)
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return post_pb2.PostResponse(
                    success=False,
                    message="Post not found"
                )

            for media in request.media:
                # Here you would implement media file handling
                # For now, we'll assume media_url is provided
                self.repository.add_post_media(
                    post_id=post.id,
                    media_type=media.media_type,
                    media_url="placeholder_url",  # This would be replaced with actual upload logic
                    media_order=media.media_order,
                    media_size=0,  # This would be actual file size
                    caption=media.caption
                )

            # Refresh post to get updated media
            post = self.repository.get_post(request.post_id)
            return post_pb2.PostResponse(
                success=True,
                message="Media added successfully",
                post=self._convert_to_proto_post(post)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.PostResponse(
                success=False,
                message=f"Failed to add media: {str(e)}"
            )

    def DeletePostMedia(self, request, context):
        try:
            success = self.repository.delete_post_media(request.post_id)
            if not success:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Media not found")
                return post_pb2.GenericResponse(
                    success=False,
                    message="Media not found"
                )

            return post_pb2.GenericResponse(
                success=True,
                message="Media deleted successfully"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.GenericResponse(
                success=False,
                message=f"Failed to delete media: {str(e)}"
            )

    def LikePost(self, request, context):
        try:
            post = self.repository.like_post(
                post_id=request.id,
                user_id=request.user_id,
                reaction_type=request.reaction_type
            )
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return post_pb2.PostResponse(
                    success=False,
                    message="Post not found"
                )

            return post_pb2.PostResponse(
                success=True,
                message="Post liked successfully",
                post=self._convert_to_proto_post(post)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.PostResponse(
                success=False,
                message=f"Failed to like post: {str(e)}"
            )

    def UnlikePost(self, request, context):
        try:
            post = self.repository.unlike_post(
                post_id=request.id,
                user_id=request.user_id
            )
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return post_pb2.PostResponse(
                    success=False,
                    message="Post not found"
                )

            return post_pb2.PostResponse(
                success=True,
                message="Post unliked successfully",
                post=self._convert_to_proto_post(post)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.PostResponse(
                success=False,
                message=f"Failed to unlike post: {str(e)}"
            )

    def CreateComment(self, request, context):
        try:
            # First check if user exists
            user = self.db.query(UserReference).filter(UserReference.id == request.user_id).first()
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with id {request.user_id} not found")
                return post_pb2.Comment()

            # Check if post exists
            post = self.repository.get_post(request.post_id)
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Post with id {request.post_id} not found")
                return post_pb2.Comment()

            # If parent_comment_id is provided, verify it exists
            if request.parent_comment_id != 0:
                parent_comment = self.db.query(CommentReference).filter(CommentReference.id == request.parent_comment_id).first()
                if not parent_comment:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"Parent comment with id {request.parent_comment_id} not found")
                    return post_pb2.Comment()
                
                # Verify parent comment belongs to the same post
                if parent_comment.post_id != request.post_id:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("Parent comment does not belong to the specified post")
                    return post_pb2.Comment()

            # Set parent_comment_id to None if it's 0 (top-level comment)
            parent_id = request.parent_comment_id if request.parent_comment_id != 0 else None

            comment = self.repository.create_comment(
                post_id=request.post_id,
                user_id=request.user_id,
                comment_text=request.comment,
                parent_comment_id=parent_id
            )

            return self._convert_to_proto_comment(comment)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.Comment()

    def UpdateComment(self, request, context):
        try:
            comment = self.repository.update_comment(
                comment_id=request.comment_id,
                comment_text=request.comment,
                status=request.status
            )
            if not comment:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Comment not found")
                return post_pb2.Comment()

            return self._convert_to_proto_comment(comment)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.Comment()

    def DeleteComment(self, request, context):
        try:
            success = self.repository.delete_comment(request.post_id)  # Using post_id as comment_id
            if not success:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Comment not found")
                return post_pb2.GenericResponse(
                    success=False,
                    message="Comment not found"
                )

            return post_pb2.GenericResponse(
                success=True,
                message="Comment deleted successfully"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.GenericResponse(
                success=False,
                message=f"Failed to delete comment: {str(e)}"
            )

    def GetComments(self, request, context):
        try:
            # Validate page number
            total_pages = (self.repository.get_post_comment_count(request.post_id) + request.limit - 1) // request.limit
            if total_pages == 0:
                total_pages = 1
            
            # If requested page is greater than total pages, return first page
            page = min(request.page, total_pages)
            if page < 1:
                page = 1

            comments, total = self.repository.get_comments(
                post_id=request.post_id,
                page=page,
                limit=request.limit
            )

            return post_pb2.CommentListResponse(
                success=True,
                message="Comments retrieved successfully",
                comments=[self._convert_to_proto_comment(c) for c in comments],
                total_count=total,
                page=page,
                total_pages=total_pages
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.CommentListResponse(
                success=False,
                message=f"Failed to get comments: {str(e)}"
            )

    def LikeComment(self, request, context):
        try:
            # First check if user exists
            user = self.db.query(UserReference).filter(UserReference.id == request.user_id).first()
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with id {request.user_id} not found")
                return post_pb2.Comment()

            comment = self.repository.like_comment(
                comment_id=request.id,
                user_id=request.user_id,
                reaction_type=request.reaction_type
            )
            if not comment:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Comment not found")
                return post_pb2.Comment()

            return self._convert_to_proto_comment(comment)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.Comment()

    def UnlikeComment(self, request, context):
        try:
            # First check if user exists
            user = self.db.query(UserReference).filter(UserReference.id == request.user_id).first()
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with id {request.user_id} not found")
                return post_pb2.Comment()

            comment = self.repository.unlike_comment(
                comment_id=request.id,
                user_id=request.user_id
            )
            if not comment:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Comment not found")
                return post_pb2.Comment()

            return self._convert_to_proto_comment(comment)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_pb2.Comment()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    post_pb2_grpc.add_PostsServiceServicer_to_server(PostsService(), server)
    server.add_insecure_port('localhost:50053')  # Using port 50053 for posts service
    server.start()
    print("Posts service started on port 50053")
    server.wait_for_termination()

if __name__ == "__main__":
    serve() 
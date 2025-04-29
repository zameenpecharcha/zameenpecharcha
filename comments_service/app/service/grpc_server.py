import grpc
from concurrent import futures
import time
from ..proto_files import comments_pb2, comments_pb2_grpc
from .comment_service import CommentService
from ..utils.db_connection import get_db

class CommentsServicer(comments_pb2_grpc.CommentsServiceServicer):
    def __init__(self):
        self.db = next(get_db())
        self.service = CommentService(self.db)

    def CreateComment(self, request, context):
        try:
            comment = self.service.create_comment(
                post_id=int(request.post_id),
                user_id=int(request.user_id),
                content=request.content,
                parent_comment_id=int(request.parent_comment_id) if request.parent_comment_id else None
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
                    created_at=comment.created_at.timestamp(),
                    updated_at=comment.updated_at.timestamp(),
                    like_count=comment.like_count
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))

    def GetComment(self, request, context):
        try:
            comment = self.service.get_comment(int(request.comment_id))
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
                    created_at=comment.created_at.timestamp(),
                    updated_at=comment.updated_at.timestamp(),
                    like_count=comment.like_count
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))

    def UpdateComment(self, request, context):
        try:
            comment = self.service.update_comment(int(request.comment_id), request.content)
            if not comment:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return comments_pb2.CommentResponse(success=False, message="Comment not found")
            
            return comments_pb2.CommentResponse(
                success=True,
                message="Comment updated successfully",
                comment=comments_pb2.Comment(
                    comment_id=str(comment.id),
                    post_id=str(comment.post_id),
                    user_id=str(comment.user_id),
                    content=comment.content,
                    parent_comment_id=str(comment.parent_comment_id) if comment.parent_comment_id else "",
                    created_at=comment.created_at.timestamp(),
                    updated_at=comment.updated_at.timestamp(),
                    like_count=comment.like_count
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))

    def DeleteComment(self, request, context):
        try:
            success = self.service.delete_comment(int(request.comment_id))
            if not success:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return comments_pb2.CommentResponse(success=False, message="Comment not found")
            
            return comments_pb2.CommentResponse(success=True, message="Comment deleted successfully")
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))

    def GetCommentsByPost(self, request, context):
        try:
            comments = self.service.get_comments_by_post(int(request.comment_id))
            return comments_pb2.CommentListResponse(
                success=True,
                message="Comments retrieved successfully",
                comments=comments_pb2.CommentList(
                    comments=[
                        comments_pb2.Comment(
                            comment_id=str(c.id),
                            post_id=str(c.post_id),
                            user_id=str(c.user_id),
                            content=c.content,
                            parent_comment_id=str(c.parent_comment_id) if c.parent_comment_id else "",
                            created_at=c.created_at.timestamp(),
                            updated_at=c.updated_at.timestamp(),
                            like_count=c.like_count
                        ) for c in comments
                    ]
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.CommentListResponse(success=False, message=str(e))

    def GetReplies(self, request, context):
        try:
            replies = self.service.get_replies(int(request.comment_id))
            return comments_pb2.CommentListResponse(
                success=True,
                message="Replies retrieved successfully",
                comments=comments_pb2.CommentList(
                    comments=[
                        comments_pb2.Comment(
                            comment_id=str(c.id),
                            post_id=str(c.post_id),
                            user_id=str(c.user_id),
                            content=c.content,
                            parent_comment_id=str(c.parent_comment_id) if c.parent_comment_id else "",
                            created_at=c.created_at.timestamp(),
                            updated_at=c.updated_at.timestamp(),
                            like_count=c.like_count
                        ) for c in replies
                    ]
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.CommentListResponse(success=False, message=str(e))

    def LikeComment(self, request, context):
        try:
            comment = self.service.like_comment(int(request.comment_id), int(request.user_id))
            if not comment:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return comments_pb2.CommentResponse(success=False, message="Comment not found")
            
            return comments_pb2.CommentResponse(
                success=True,
                message="Comment liked successfully",
                comment=comments_pb2.Comment(
                    comment_id=str(comment.id),
                    post_id=str(comment.post_id),
                    user_id=str(comment.user_id),
                    content=comment.content,
                    parent_comment_id=str(comment.parent_comment_id) if comment.parent_comment_id else "",
                    created_at=comment.created_at.timestamp(),
                    updated_at=comment.updated_at.timestamp(),
                    like_count=comment.like_count
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))

    def UnlikeComment(self, request, context):
        try:
            comment = self.service.unlike_comment(int(request.comment_id), int(request.user_id))
            if not comment:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return comments_pb2.CommentResponse(success=False, message="Comment not found")
            
            return comments_pb2.CommentResponse(
                success=True,
                message="Comment unliked successfully",
                comment=comments_pb2.Comment(
                    comment_id=str(comment.id),
                    post_id=str(comment.post_id),
                    user_id=str(comment.user_id),
                    content=comment.content,
                    parent_comment_id=str(comment.parent_comment_id) if comment.parent_comment_id else "",
                    created_at=comment.created_at.timestamp(),
                    updated_at=comment.updated_at.timestamp(),
                    like_count=comment.like_count
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.CommentResponse(success=False, message=str(e))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    comments_pb2_grpc.add_CommentsServiceServicer_to_server(CommentsServicer(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    print("Comments gRPC server started on port 50053")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve() 
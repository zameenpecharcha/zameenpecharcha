import typing
import strawberry
from app.exception.UserException import REException
from app.utils.log_utils import log_msg
from app.utils.grpc_client import comments_client

@strawberry.type
class Comment:
    commentId: str = strawberry.field(name="commentId")
    postId: str = strawberry.field(name="postId")
    userId: str = strawberry.field(name="userId")
    content: str
    parentCommentId: typing.Optional[str] = strawberry.field(name="parentCommentId")
    createdAt: int = strawberry.field(name="createdAt")
    updatedAt: int = strawberry.field(name="updatedAt")
    likeCount: int = strawberry.field(name="likeCount")

@strawberry.type
class Query:
    @strawberry.field
    def comment(self, commentId: str) -> typing.Optional[Comment]:
        try:
            response = comments_client.get_comment(commentId)
            if response.success:
                return Comment(
                    commentId=response.comment.comment_id,
                    postId=response.comment.post_id,
                    userId=response.comment.user_id,
                    content=response.comment.content,
                    parentCommentId=response.comment.parent_comment_id,
                    createdAt=response.comment.created_at,
                    updatedAt=response.comment.updated_at,
                    likeCount=response.comment.like_count
                )
            return None
        except Exception as e:
            log_msg("error", f"Error fetching comment: {str(e)}")
            raise REException(
                "COMMENT_NOT_FOUND",
                "Failed to fetch comment",
                str(e)
            ).to_graphql_error()

    @strawberry.field
    def commentsByPost(self, postId: str) -> typing.List[Comment]:
        try:
            response = comments_client.get_comments_by_post(postId)
            if response.success:
                return [
                    Comment(
                        commentId=comment.comment_id,
                        postId=comment.post_id,
                        userId=comment.user_id,
                        content=comment.content,
                        parentCommentId=comment.parent_comment_id,
                        createdAt=comment.created_at,
                        updatedAt=comment.updated_at,
                        likeCount=comment.like_count
                    )
                    for comment in response.comments.comments
                ]
            return []
        except Exception as e:
            log_msg("error", f"Error fetching comments: {str(e)}")
            raise REException(
                "COMMENTS_FETCH_FAILED",
                "Failed to fetch comments",
                str(e)
            ).to_graphql_error()

    @strawberry.field
    def commentReplies(self, commentId: str) -> typing.List[Comment]:
        try:
            response = comments_client.get_replies(commentId)
            if response.success:
                return [
                    Comment(
                        commentId=comment.comment_id,
                        postId=comment.post_id,
                        userId=comment.user_id,
                        content=comment.content,
                        parentCommentId=comment.parent_comment_id,
                        createdAt=comment.created_at,
                        updatedAt=comment.updated_at,
                        likeCount=comment.like_count
                    )
                    for comment in response.comments.comments
                ]
            return []
        except Exception as e:
            log_msg("error", f"Error fetching replies: {str(e)}")
            raise REException(
                "REPLIES_FETCH_FAILED",
                "Failed to fetch replies",
                str(e)
            ).to_graphql_error()

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def createComment(
        self, postId: str, userId: str, content: str, parentCommentId: typing.Optional[str] = None
    ) -> Comment:
        try:
            response = comments_client.create_comment(postId, userId, content, parentCommentId)
            if response.success:
                return Comment(
                    commentId=response.comment.comment_id,
                    postId=response.comment.post_id,
                    userId=response.comment.user_id,
                    content=response.comment.content,
                    parentCommentId=response.comment.parent_comment_id,
                    createdAt=response.comment.created_at,
                    updatedAt=response.comment.updated_at,
                    likeCount=response.comment.like_count
                )
            raise REException(
                "COMMENT_CREATION_FAILED",
                response.message,
                "Failed to create comment"
            ).to_graphql_error()
        except Exception as e:
            log_msg("error", f"Error creating comment: {str(e)}")
            raise REException(
                "COMMENT_CREATION_FAILED",
                "Failed to create comment",
                str(e)
            ).to_graphql_error()

    @strawberry.mutation
    async def updateComment(self, commentId: str, content: str) -> Comment:
        try:
            response = comments_client.update_comment(commentId, content)
            if response.success:
                return Comment(
                    commentId=response.comment.comment_id,
                    postId=response.comment.post_id,
                    userId=response.comment.user_id,
                    content=response.comment.content,
                    parentCommentId=response.comment.parent_comment_id,
                    createdAt=response.comment.created_at,
                    updatedAt=response.comment.updated_at,
                    likeCount=response.comment.like_count
                )
            raise REException(
                "COMMENT_UPDATE_FAILED",
                response.message,
                "Failed to update comment"
            ).to_graphql_error()
        except Exception as e:
            log_msg("error", f"Error updating comment: {str(e)}")
            raise REException(
                "COMMENT_UPDATE_FAILED",
                "Failed to update comment",
                str(e)
            ).to_graphql_error()

    @strawberry.mutation
    async def deleteComment(self, commentId: str) -> bool:
        try:
            response = comments_client.delete_comment(commentId)
            return response.success
        except Exception as e:
            log_msg("error", f"Error deleting comment: {str(e)}")
            raise REException(
                "COMMENT_DELETION_FAILED",
                "Failed to delete comment",
                str(e)
            ).to_graphql_error()

    @strawberry.mutation
    async def likeComment(self, commentId: str, userId: str) -> Comment:
        try:
            response = comments_client.like_comment(commentId, userId)
            if response.success:
                return Comment(
                    commentId=response.comment.comment_id,
                    postId=response.comment.post_id,
                    userId=response.comment.user_id,
                    content=response.comment.content,
                    parentCommentId=response.comment.parent_comment_id,
                    createdAt=response.comment.created_at,
                    updatedAt=response.comment.updated_at,
                    likeCount=response.comment.like_count
                )
            raise REException(
                "COMMENT_LIKE_FAILED",
                response.message,
                "Failed to like comment"
            ).to_graphql_error()
        except Exception as e:
            log_msg("error", f"Error liking comment: {str(e)}")
            raise REException(
                "COMMENT_LIKE_FAILED",
                "Failed to like comment",
                str(e)
            ).to_graphql_error()

    @strawberry.mutation
    async def unlikeComment(self, commentId: str, userId: str) -> Comment:
        try:
            response = comments_client.unlike_comment(commentId, userId)
            if response.success:
                return Comment(
                    commentId=response.comment.comment_id,
                    postId=response.comment.post_id,
                    userId=response.comment.user_id,
                    content=response.comment.content,
                    parentCommentId=response.comment.parent_comment_id,
                    createdAt=response.comment.created_at,
                    updatedAt=response.comment.updated_at,
                    likeCount=response.comment.like_count
                )
            raise REException(
                "COMMENT_UNLIKE_FAILED",
                response.message,
                "Failed to unlike comment"
            ).to_graphql_error()
        except Exception as e:
            log_msg("error", f"Error unliking comment: {str(e)}")
            raise REException(
                "COMMENT_UNLIKE_FAILED",
                "Failed to unlike comment",
                str(e)
            ).to_graphql_error() 
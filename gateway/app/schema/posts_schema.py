import typing
import strawberry
from app.exception.UserException import REException
from app.utils.log_utils import log_msg
from app.utils.grpc_client import posts_client

@strawberry.type
class Post:
    postId: str = strawberry.field(name="postId")
    userId: str = strawberry.field(name="userId")
    title: str
    content: str
    createdAt: int = strawberry.field(name="createdAt")
    updatedAt: int = strawberry.field(name="updatedAt")
    likeCount: int = strawberry.field(name="likeCount")
    commentCount: int = strawberry.field(name="commentCount")

@strawberry.type
class Query:
    @strawberry.field
    def post(self, postId: str) -> typing.Optional[Post]:
        try:
            response = posts_client.get_post(postId)
            if not response.success:
                raise REException("POST_NOT_FOUND", response.message, "Post not found")
            
            return Post(
                postId=response.post.post_id,
                userId=response.post.user_id,
                title=response.post.title,
                content=response.post.content,
                createdAt=response.post.created_at,
                updatedAt=response.post.updated_at,
                likeCount=response.post.like_count,
                commentCount=response.post.comment_count
            )
        except Exception as e:
            log_msg("error", f"Error fetching post: {str(e)}")
            raise REException(
                "POST_NOT_FOUND",
                "Failed to fetch post",
                str(e)
            ).to_graphql_error()

    @strawberry.field
    def posts_by_user(self, userId: str) -> typing.List[Post]:
        try:
            response = posts_client.get_posts_by_user(userId)
            if not response.success:
                raise REException("POSTS_NOT_FOUND", response.message, "Failed to fetch posts")
            
            return [
                Post(
                    postId=post.post_id,
                    userId=post.user_id,
                    title=post.title,
                    content=post.content,
                    createdAt=post.created_at,
                    updatedAt=post.updated_at,
                    likeCount=post.like_count,
                    commentCount=post.comment_count
                )
                for post in response.posts.posts
            ]
        except Exception as e:
            log_msg("error", f"Error fetching posts: {str(e)}")
            raise REException(
                "POSTS_NOT_FOUND",
                "Failed to fetch posts",
                str(e)
            ).to_graphql_error()

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_post(
        self, userId: str, title: str, content: str
    ) -> Post:
        try:
            response = posts_client.create_post(userId, title, content)
            if not response.success:
                raise REException("POST_CREATION_FAILED", response.message, "Failed to create post")
            
            return Post(
                postId=response.post.post_id,
                userId=response.post.user_id,
                title=response.post.title,
                content=response.post.content,
                createdAt=response.post.created_at,
                updatedAt=response.post.updated_at,
                likeCount=response.post.like_count,
                commentCount=response.post.comment_count
            )
        except Exception as e:
            log_msg("error", f"Error creating post: {str(e)}")
            raise REException(
                "POST_CREATION_FAILED",
                "Failed to create post",
                str(e)
            ).to_graphql_error()

    @strawberry.mutation
    async def update_post(
        self, postId: str, title: str, content: str
    ) -> Post:
        try:
            response = posts_client.update_post(postId, title, content)
            if not response.success:
                raise REException("POST_UPDATE_FAILED", response.message, "Failed to update post")
            
            return Post(
                postId=response.post.post_id,
                userId=response.post.user_id,
                title=response.post.title,
                content=response.post.content,
                createdAt=response.post.created_at,
                updatedAt=response.post.updated_at,
                likeCount=response.post.like_count,
                commentCount=response.post.comment_count
            )
        except Exception as e:
            log_msg("error", f"Error updating post: {str(e)}")
            raise REException(
                "POST_UPDATE_FAILED",
                "Failed to update post",
                str(e)
            ).to_graphql_error()

    @strawberry.mutation
    async def delete_post(self, postId: str) -> bool:
        try:
            response = posts_client.delete_post(postId)
            if not response.success:
                raise REException("POST_DELETION_FAILED", response.message, "Failed to delete post")
            return True
        except Exception as e:
            log_msg("error", f"Error deleting post: {str(e)}")
            raise REException(
                "POST_DELETION_FAILED",
                "Failed to delete post",
                str(e)
            ).to_graphql_error()

    @strawberry.mutation
    async def like_post(self, postId: str, userId: str) -> Post:
        try:
            response = posts_client.like_post(postId, userId)
            if not response.success:
                raise REException("POST_LIKE_FAILED", response.message, "Failed to like post")
            
            return Post(
                postId=response.post.post_id,
                userId=response.post.user_id,
                title=response.post.title,
                content=response.post.content,
                createdAt=response.post.created_at,
                updatedAt=response.post.updated_at,
                likeCount=response.post.like_count,
                commentCount=response.post.comment_count
            )
        except Exception as e:
            log_msg("error", f"Error liking post: {str(e)}")
            raise REException(
                "POST_LIKE_FAILED",
                "Failed to like post",
                str(e)
            ).to_graphql_error()

    @strawberry.mutation
    async def unlike_post(self, postId: str, userId: str) -> Post:
        try:
            response = posts_client.unlike_post(postId, userId)
            if not response.success:
                raise REException("POST_UNLIKE_FAILED", response.message, "Failed to unlike post")
            
            return Post(
                postId=response.post.post_id,
                userId=response.post.user_id,
                title=response.post.title,
                content=response.post.content,
                createdAt=response.post.created_at,
                updatedAt=response.post.updated_at,
                likeCount=response.post.like_count,
                commentCount=response.post.comment_count
            )
        except Exception as e:
            log_msg("error", f"Error unliking post: {str(e)}")
            raise REException(
                "POST_UNLIKE_FAILED",
                "Failed to unlike post",
                str(e)
            ).to_graphql_error() 
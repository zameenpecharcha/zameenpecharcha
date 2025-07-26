import strawberry
from typing import List, Optional
from datetime import datetime
from ..utils.grpc_client import PostsServiceClient

@strawberry.type
class PostMedia:
    id: int
    post_id: int
    media_type: str
    media_url: str
    media_order: int
    media_size: int
    caption: Optional[str]
    uploaded_at: datetime

@strawberry.type
class Comment:
    id: int
    post_id: int
    parent_comment_id: Optional[int]
    comment: str
    user_id: int
    status: str
    added_at: datetime
    commented_at: datetime
    replies: List['Comment']
    like_count: int

@strawberry.type
class Post:
    id: int
    user_id: int
    title: str
    content: str
    visibility: Optional[str]
    property_type: Optional[str]
    location: Optional[str]
    map_location: Optional[str]
    price: Optional[float]
    status: Optional[str]
    created_at: datetime
    media: List[PostMedia]
    comments: List[Comment]
    like_count: int
    comment_count: int

@strawberry.type
class PostResponse:
    success: bool
    message: str
    post: Optional[Post]

@strawberry.type
class PostListResponse:
    success: bool
    message: str
    posts: List[Post]
    total_count: int
    page: int
    total_pages: int

@strawberry.type
class CommentListResponse:
    success: bool
    message: str
    comments: List[Comment]
    total_count: int
    page: int
    total_pages: int

@strawberry.type
class GenericResponse:
    success: bool
    message: str

@strawberry.input
class PostMediaInput:
    media_type: str
    media_data: str
    media_order: int
    caption: Optional[str]

@strawberry.type
class Query:
    @strawberry.field
    def post(self, post_id: int) -> PostResponse:
        client = PostsServiceClient()
        response = client.get_post(post_id)
        return PostResponse(
            success=response.success,
            message=response.message,
            post=response.post if response.success else None
        )

    @strawberry.field
    def posts_by_user(self, user_id: int, page: int = 1, limit: int = 10) -> PostListResponse:
        client = PostsServiceClient()
        response = client.get_posts_by_user(user_id, page, limit)
        return PostListResponse(
            success=response.success,
            message=response.message,
            posts=response.posts,
            total_count=response.total_count,
            page=response.page,
            total_pages=response.total_pages
        )

    @strawberry.field
    def search_posts(self, property_type: Optional[str] = None, location: Optional[str] = None,
                    min_price: Optional[float] = None, max_price: Optional[float] = None,
                    status: Optional[str] = None, page: int = 1, limit: int = 10) -> PostListResponse:
        client = PostsServiceClient()
        response = client.search_posts(
            property_type=property_type,
            location=location,
            min_price=min_price,
            max_price=max_price,
            status=status,
            page=page,
            limit=limit
        )
        return PostListResponse(
            success=response.success,
            message=response.message,
            posts=response.posts,
            total_count=response.total_count,
            page=response.page,
            total_pages=response.total_pages
        )

    @strawberry.field
    def post_comments(self, post_id: int, page: int = 1, limit: int = 10) -> CommentListResponse:
        client = PostsServiceClient()
        response = client.get_comments(post_id, page, limit)
        return CommentListResponse(
            success=response.success,
            message=response.message,
            comments=response.comments,
            total_count=response.total_count,
            page=response.page,
            total_pages=response.total_pages
        )

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_post(self, user_id: int, title: str, content: str,
                   visibility: Optional[str] = None, property_type: Optional[str] = None,
                   location: Optional[str] = None, map_location: Optional[str] = None,
                   price: Optional[float] = None, status: Optional[str] = None,
                   media: Optional[List[PostMediaInput]] = None) -> PostResponse:
        client = PostsServiceClient()
        response = client.create_post(
            user_id=user_id,
            title=title,
            content=content,
            visibility=visibility,
            property_type=property_type,
            location=location,
            map_location=map_location,
            price=price,
            status=status,
            media=[{
                'media_type': m.media_type,
                'media_data': m.media_data,
                'media_order': m.media_order,
                'caption': m.caption
            } for m in (media or [])]
        )
        return PostResponse(
            success=response.success,
            message=response.message,
            post=response.post if response.success else None
        )

    @strawberry.mutation
    def update_post(self, post_id: int, title: Optional[str] = None,
                   content: Optional[str] = None, visibility: Optional[str] = None,
                   property_type: Optional[str] = None, location: Optional[str] = None,
                   map_location: Optional[str] = None, price: Optional[float] = None,
                   status: Optional[str] = None) -> PostResponse:
        client = PostsServiceClient()
        response = client.update_post(
            post_id=post_id,
            title=title,
            content=content,
            visibility=visibility,
            property_type=property_type,
            location=location,
            map_location=map_location,
            price=price,
            status=status
        )
        return PostResponse(
            success=response.success,
            message=response.message,
            post=response.post if response.success else None
        )

    @strawberry.mutation
    def delete_post(self, post_id: int) -> GenericResponse:
        client = PostsServiceClient()
        response = client.delete_post(post_id)
        return GenericResponse(
            success=response.success,
            message=response.message
        )

    @strawberry.mutation
    def add_post_media(self, post_id: int, media: List[PostMediaInput]) -> PostResponse:
        client = PostsServiceClient()
        response = client.add_post_media(
            post_id=post_id,
            media=[{
                'media_type': m.media_type,
                'media_data': m.media_data,
                'media_order': m.media_order,
                'caption': m.caption
            } for m in media]
        )
        return PostResponse(
            success=response.success,
            message=response.message,
            post=response.post if response.success else None
        )

    @strawberry.mutation
    def delete_post_media(self, media_id: int) -> GenericResponse:
        client = PostsServiceClient()
        response = client.delete_post_media(media_id)
        return GenericResponse(
            success=response.success,
            message=response.message
        )

    @strawberry.mutation
    def like_post(self, post_id: int, user_id: int, reaction_type: str = 'like') -> PostResponse:
        client = PostsServiceClient()
        response = client.like_post(post_id, user_id, reaction_type)
        return PostResponse(
            success=response.success,
            message=response.message,
            post=response.post if response.success else None
        )

    @strawberry.mutation
    def unlike_post(self, post_id: int, user_id: int) -> PostResponse:
        client = PostsServiceClient()
        response = client.unlike_post(post_id, user_id)
        return PostResponse(
            success=response.success,
            message=response.message,
            post=response.post if response.success else None
        )

    @strawberry.mutation
    def create_comment(self, post_id: int, user_id: int, comment: str,
                      parent_comment_id: Optional[int] = None) -> Comment:
        client = PostsServiceClient()
        return client.create_comment(post_id, user_id, comment, parent_comment_id)

    @strawberry.mutation
    def update_comment(self, comment_id: int, comment: Optional[str] = None,
                      status: Optional[str] = None) -> Comment:
        client = PostsServiceClient()
        return client.update_comment(comment_id, comment, status)

    @strawberry.mutation
    def delete_comment(self, comment_id: int) -> GenericResponse:
        client = PostsServiceClient()
        response = client.delete_comment(comment_id)
        return GenericResponse(
            success=response.success,
            message=response.message
        )

    @strawberry.mutation
    def like_comment(self, comment_id: int, user_id: int, reaction_type: str = 'like') -> Comment:
        client = PostsServiceClient()
        return client.like_comment(comment_id, user_id, reaction_type)

    @strawberry.mutation
    def unlike_comment(self, comment_id: int, user_id: int) -> Comment:
        client = PostsServiceClient()
        return client.unlike_comment(comment_id, user_id) 
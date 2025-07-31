import strawberry
from typing import List, Optional
from datetime import datetime
from ..utils.grpc_client import PostsServiceClient
import logging
from dataclasses import dataclass
import typing

logger = logging.getLogger(__name__)

@strawberry.type
class Comment:
    id: int
    postId: int
    userId: int
    userFirstName: str
    userLastName: str
    userRole: str
    comment: str
    parentCommentId: Optional[int]
    status: str
    addedAt: datetime
    commentedAt: datetime
    replies: List['Comment']
    likeCount: int

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return None
        return cls(
            id=data['id'],
            postId=data['postId'],
            userId=data['userId'],
            userFirstName=data.get('userFirstName', ''),
            userLastName=data.get('userLastName', ''),
            userRole=data.get('userRole', ''),
            comment=data['comment'],
            parentCommentId=data.get('parentCommentId'),
            status=data['status'],
            addedAt=data['addedAt'],
            commentedAt=data['commentedAt'],
            replies=[cls.from_dict(reply) for reply in data.get('replies', [])],
            likeCount=data['likeCount']
        )

@strawberry.type
class CommentResponse:
    success: bool
    message: str
    comment: Optional[Comment] = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            success=data['success'],
            message=data['message'],
            comment=Comment.from_dict(data.get('comment'))
        )

@strawberry.type
class PostMedia:
    id: int
    mediaType: str
    mediaUrl: str
    mediaOrder: int
    mediaSize: Optional[int]
    caption: Optional[str]
    uploadedAt: datetime

@strawberry.input
class PostMediaInput:
    mediaType: str
    mediaData: str
    mediaOrder: int
    caption: Optional[str] = None

@strawberry.type
class Post:
    id: int
    userId: int
    userFirstName: str
    userLastName: str
    userEmail: str
    userPhone: str
    userRole: str
    title: str
    content: str
    visibility: str
    propertyType: str
    location: str
    mapLocation: str
    price: float
    status: str
    createdAt: datetime
    media: List[PostMedia]
    likeCount: int
    commentCount: int

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return None
        media_list = [
            PostMedia(
                id=m['id'],
                mediaType=m['mediaType'],
                mediaUrl=m['mediaUrl'],
                mediaOrder=m['mediaOrder'],
                mediaSize=m.get('mediaSize'),
                caption=m.get('caption'),
                uploadedAt=m['uploadedAt']
            ) for m in data.get('media', [])
        ]
        return cls(
            id=data['id'],
            userId=data['userId'],
            userFirstName=data.get('userFirstName', ''),
            userLastName=data.get('userLastName', ''),
            userEmail=data.get('userEmail', ''),
            userPhone=data.get('userPhone', ''),
            userRole=data.get('userRole', ''),
            title=data['title'],
            content=data['content'],
            visibility=data['visibility'],
            propertyType=data['propertyType'],
            location=data['location'],
            mapLocation=data['mapLocation'],
            price=data['price'],
            status=data['status'],
            createdAt=data['createdAt'],
            media=media_list,
            likeCount=data['likeCount'],
            commentCount=data['commentCount']
        )

@strawberry.type
class PostResponse:
    success: bool
    message: str
    post: Optional[Post] = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            success=data['success'],
            message=data['message'],
            post=Post.from_dict(data.get('post'))
        )

@strawberry.type
class Query:
    @strawberry.field
    def post(self, postId: int) -> Optional[Post]:
        logger.debug(f"Query.post called with postId: {postId}")
        client = PostsServiceClient()
        result = client.get_post(post_id=postId)
        # Convert gRPC response to dictionary format
        if result and result.success and result.post:
            post_data = {
                'id': result.post.id,
                'userId': result.post.user_id,
                'title': result.post.title,
                'content': result.post.content,
                'visibility': result.post.visibility,
                'propertyType': result.post.property_type,
                'location': result.post.location,
                'mapLocation': result.post.map_location,
                'price': result.post.price,
                'status': result.post.status,
                'createdAt': datetime.fromtimestamp(result.post.created_at),
                'media': [{
                    'id': m.id,
                    'mediaType': m.media_type,
                    'mediaUrl': m.media_url,
                    'mediaOrder': m.media_order,
                    'mediaSize': m.media_size,
                    'caption': m.caption,
                    'uploadedAt': datetime.fromtimestamp(m.uploaded_at)
                } for m in result.post.media],
                'likeCount': result.post.like_count,
                'commentCount': result.post.comment_count
            }
            return Post.from_dict(post_data)
        return None

    @strawberry.field
    def postsByUser(self, userId: int, page: int = 1, limit: int = 10) -> List[Post]:
        logger.debug(f"Query.postsByUser called with userId: {userId}, page: {page}, limit: {limit}")
        client = PostsServiceClient()
        result = client.get_posts_by_user(user_id=userId, page=page, limit=limit)
        return [Post.from_dict(post) for post in result] if result else []

    @strawberry.field
    def searchPosts(
        self,
        propertyType: Optional[str] = None,
        location: Optional[str] = None,
        minPrice: Optional[float] = None,
        maxPrice: Optional[float] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> List[Post]:
        logger.debug(f"Query.searchPosts called with propertyType: {propertyType}, location: {location}")
        client = PostsServiceClient()
        result = client.search_posts(
            property_type=propertyType,
            location=location,
            min_price=minPrice,
            max_price=maxPrice,
            status=status,
            page=page,
            limit=limit
        )
        
        if not result or not result.success:
            logger.error("No result or unsuccessful response")
            return []
            
        posts_data = []
        for post in result.posts:
            logger.debug(f"Processing post: {post}")
            post_dict = {
                'id': post.id,
                'userId': post.user_id,
                'userFirstName': getattr(post, 'user_first_name', ''),
                'userLastName': getattr(post, 'user_last_name', ''),
                'userEmail': getattr(post, 'user_email', ''),
                'userPhone': getattr(post, 'user_phone', ''),
                'userRole': getattr(post, 'user_role', ''),
                'title': post.title,
                'content': post.content,
                'visibility': post.visibility,
                'propertyType': post.property_type,
                'location': post.location,
                'mapLocation': post.map_location,
                'price': post.price,
                'status': post.status,
                'createdAt': datetime.fromtimestamp(post.created_at),
                'media': [{
                    'id': m.id,
                    'mediaType': m.media_type,
                    'mediaUrl': m.media_url,
                    'mediaOrder': m.media_order,
                    'mediaSize': m.media_size,
                    'caption': m.caption,
                    'uploadedAt': datetime.fromtimestamp(m.uploaded_at)
                } for m in post.media],
                'likeCount': post.like_count,
                'commentCount': post.comment_count
            }
            logger.debug(f"Created post dict: {post_dict}")
            posts_data.append(post_dict)
            
        posts = [Post.from_dict(post) for post in posts_data]
        logger.debug(f"Returning {len(posts)} posts")
        return posts

    @strawberry.field
    def postComments(
        self,
        postId: int,
        page: int = 1,
        limit: int = 10
    ) -> List[Comment]:
        logger.debug(f"Query.postComments called with postId: {postId}")
        client = PostsServiceClient()
        result = client.get_comments(post_id=postId, page=page, limit=limit)
        
        if not result or not result.success:
            return []
            
        comments_data = []
        for comment in result.comments:
            comment_dict = {
                'id': comment.id,
                'postId': comment.post_id,
                'userId': comment.user_id,
                'userFirstName': comment.user_first_name,
                'userLastName': comment.user_last_name,
                'userRole': comment.user_role,
                'comment': comment.comment,
                'parentCommentId': comment.parent_comment_id if comment.parent_comment_id != 0 else None,
                'status': comment.status,
                'addedAt': datetime.fromtimestamp(comment.added_at),
                'commentedAt': datetime.fromtimestamp(comment.commented_at),
                'replies': [
                    {
                        'id': r.id,
                        'postId': r.post_id,
                        'userId': r.user_id,
                        'userFirstName': r.user_first_name,
                        'userLastName': r.user_last_name,
                        'userRole': r.user_role,
                        'comment': r.comment,
                        'parentCommentId': r.parent_comment_id,
                        'status': r.status,
                        'addedAt': datetime.fromtimestamp(r.added_at),
                        'commentedAt': datetime.fromtimestamp(r.commented_at),
                        'replies': [],
                        'likeCount': r.like_count
                    } for r in comment.replies
                ],
                'likeCount': comment.like_count
            }
            comments_data.append(comment_dict)
            
        return [Comment.from_dict(comment) for comment in comments_data]

@strawberry.type
class MediaResponse:
    success: bool
    message: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            success=data['success'],
            message=data['message']
        )

@strawberry.type
class Mutation:
    @strawberry.mutation
    def createPost(
        self,
        userId: int,
        title: str,
        content: str,
        visibility: str,
        propertyType: str,
        location: str,
        mapLocation: str,
        price: float,
        status: str,
        media: typing.Optional[typing.List[PostMediaInput]] = None
    ) -> PostResponse:
        logger.debug(f"Mutation.createPost called with userId: {userId}, title: {title}")
        client = PostsServiceClient()
        result = client.create_post(
            user_id=userId,
            title=title,
            content=content,
            visibility=visibility,
            property_type=propertyType,
            location=location,
            map_location=mapLocation,
            price=price,
            status=status,
            media=media or []
        )
        logger.debug(f"CreatePost result: {result}")
        return PostResponse.from_dict(result)

    @strawberry.mutation
    def updatePost(
        self,
        postId: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        visibility: Optional[str] = None,
        propertyType: Optional[str] = None,
        location: Optional[str] = None,
        mapLocation: Optional[str] = None,
        price: Optional[float] = None,
        status: Optional[str] = None
    ) -> PostResponse:
        logger.debug(f"Mutation.updatePost called with postId: {postId}")
        client = PostsServiceClient()
        result = client.update_post(
            post_id=postId,
            title=title,
            content=content,
            visibility=visibility,
            property_type=propertyType,
            location=location,
            map_location=mapLocation,
            price=price,
            status=status
        )
        return PostResponse.from_dict(result)

    @strawberry.mutation
    def deletePost(self, postId: int) -> PostResponse:
        logger.debug(f"Mutation.deletePost called with postId: {postId}")
        client = PostsServiceClient()
        result = client.delete_post(post_id=postId)
        return PostResponse.from_dict(result)

    @strawberry.mutation
    def likePost(self, postId: int, userId: int) -> PostResponse:
        logger.debug(f"Mutation.likePost called with postId: {postId}, userId: {userId}")
        client = PostsServiceClient()
        result = client.like_post(post_id=postId, user_id=userId)
        return PostResponse.from_dict(result)

    @strawberry.mutation
    def unlikePost(self, postId: int, userId: int) -> PostResponse:
        logger.debug(f"Mutation.unlikePost called with postId: {postId}, userId: {userId}")
        client = PostsServiceClient()
        result = client.unlike_post(post_id=postId, user_id=userId)
        return PostResponse.from_dict(result)

    @strawberry.mutation
    def createComment(
        self,
        postId: int,
        userId: int,
        comment: str,
        parentCommentId: Optional[int] = None
    ) -> CommentResponse:
        logger.debug(f"Mutation.createComment called with postId: {postId}, userId: {userId}")
        client = PostsServiceClient()
        result = client.create_comment(
            post_id=postId,
            user_id=userId,
            comment=comment,
            parent_comment_id=parentCommentId
        )
        logger.debug(f"CreateComment result: {result}")
        return CommentResponse.from_dict(result)

    @strawberry.mutation
    def updateComment(
        self,
        commentId: int,
        comment: Optional[str] = None,
        status: Optional[str] = None
    ) -> CommentResponse:
        logger.debug(f"Mutation.updateComment called with commentId: {commentId}")
        client = PostsServiceClient()
        result = client.update_comment(
            comment_id=commentId,
            comment=comment,
            status=status
        )
        return CommentResponse.from_dict(result)

    @strawberry.mutation
    def deleteComment(
        self,
        commentId: int
    ) -> CommentResponse:
        logger.debug(f"Mutation.deleteComment called with commentId: {commentId}")
        client = PostsServiceClient()
        result = client.delete_comment(comment_id=commentId)
        return CommentResponse.from_dict(result)

    @strawberry.mutation
    def likeComment(
        self,
        commentId: int,
        userId: int
    ) -> CommentResponse:
        logger.debug(f"Mutation.likeComment called with commentId: {commentId}, userId: {userId}")
        client = PostsServiceClient()
        result = client.like_comment(
            comment_id=commentId,
            user_id=userId
        )
        return CommentResponse.from_dict(result)

    @strawberry.mutation
    def unlikeComment(
        self,
        commentId: int,
        userId: int
    ) -> CommentResponse:
        logger.debug(f"Mutation.unlikeComment called with commentId: {commentId}, userId: {userId}")
        client = PostsServiceClient()
        result = client.unlike_comment(
            comment_id=commentId,
            user_id=userId
        )
        return CommentResponse.from_dict(result)

    @strawberry.mutation
    def addPostMedia(
        self,
        postId: int,
        media: List[PostMediaInput]
    ) -> PostResponse:
        logger.debug(f"Mutation.addPostMedia called with postId: {postId}")
        client = PostsServiceClient()
        result = client.add_post_media(
            post_id=postId,
            media=media
        )
        return PostResponse.from_dict(result)

    @strawberry.mutation
    def deletePostMedia(
        self,
        mediaId: int
    ) -> MediaResponse:
        logger.debug(f"Mutation.deletePostMedia called with mediaId: {mediaId}")
        client = PostsServiceClient()
        result = client.delete_post_media(media_id=mediaId)
        return MediaResponse.from_dict(result) 
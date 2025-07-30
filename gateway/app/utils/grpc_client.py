import grpc
import sys
import os
from pathlib import Path
from app.utils.log_utils import log_msg
import base64
from datetime import datetime
from typing import Optional

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from app.proto_files.auth import auth_pb2_grpc, auth_pb2
from app.proto_files.user import user_pb2_grpc, user_pb2
from app.proto_files.posts import post_pb2_grpc, post_pb2
import app.proto_files.comments.comments_pb2 as comments_pb2
import app.proto_files.comments.comments_pb2_grpc as comments_pb2_grpc
from app.proto_files.property import property_pb2, property_pb2_grpc

class AuthServiceClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50052')
        self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)

    def login(self, email: str, password: str):
        try:
            request = auth_pb2.LoginRequest(
                email=email,
                password=password
            )
            return self.stub.Login(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in login: {str(e)}")
            raise e

    def send_otp(self, email: str, phone: str = None, otp_type: int = 0):
        try:
            request = auth_pb2.OTPRequest(
                email=email,
                phone=phone,
                type=otp_type.value if hasattr(otp_type, 'value') else otp_type
            )
            return self.stub.SendOTP(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in send_otp: {str(e)}")
            raise e

    def verify_otp(self, email: str, otp_code: str, otp_type: int = 0):
        try:
            request = auth_pb2.VerifyOTPRequest(
                email=email,
                otp_code=otp_code,
                type=otp_type.value if hasattr(otp_type, 'value') else otp_type
            )
            return self.stub.VerifyOTP(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in verify_otp: {str(e)}")
            raise e

    def forgot_password(self, email: str, phone: str = None):
        try:
            request = auth_pb2.ForgotPasswordRequest(
                email=email,
                phone=phone
            )
            return self.stub.ForgotPassword(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in forgot_password: {str(e)}")
            raise e

    def reset_password(self, email: str, otp_code: str, new_password: str, confirm_password: str):
        try:
            request = auth_pb2.ResetPasswordRequest(
                email=email,
                otp_code=otp_code,
                new_password=new_password,
                confirm_password=confirm_password
            )
            return self.stub.ResetPassword(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in reset_password: {str(e)}")
            raise e

class UserServiceClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = user_pb2_grpc.UserServiceStub(self.channel)

    def get_user(self, id):
        try:
            request = user_pb2.UserRequest(id=id)
            return self.stub.GetUser(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in get_user: {str(e)}")
            raise e

    def create_user(self, first_name, last_name, email, phone, password, role=None, 
                   address=None, latitude=None, longitude=None, bio=None):
        try:
            request = user_pb2.CreateUserRequest(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                password=password,
                role=role,
                address=address,
                latitude=latitude,
                longitude=longitude,
                bio=bio
            )
            return self.stub.CreateUser(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in create_user: {str(e)}")
            raise e

    def create_user_rating(self, rated_user_id, rated_by_user_id, rating_value, review=None, rating_type=None):
        try:
            request = user_pb2.CreateUserRatingRequest(
                rated_user_id=rated_user_id,
                rated_by_user_id=rated_by_user_id,
                rating_value=rating_value,
                review=review,
                rating_type=rating_type
            )
            return self.stub.CreateUserRating(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in create_user_rating: {str(e)}")
            raise e

    def get_user_ratings(self, user_id):
        try:
            request = user_pb2.UserRequest(id=user_id)
            return self.stub.GetUserRatings(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in get_user_ratings: {str(e)}")
            raise e

    def follow_user(self, user_id, following_id):
        try:
            request = user_pb2.FollowUserRequest(
                user_id=user_id,
                following_id=following_id
            )
            return self.stub.FollowUser(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in follow_user: {str(e)}")
            raise e

    def get_user_followers(self, user_id):
        try:
            request = user_pb2.UserRequest(id=user_id)
            return self.stub.GetUserFollowers(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in get_user_followers: {str(e)}")
            raise e

    def get_user_following(self, user_id):
        try:
            request = user_pb2.UserRequest(id=user_id)
            return self.stub.GetUserFollowing(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in get_user_following: {str(e)}")
            raise e

    def check_following_status(self, user_id, following_id):
        try:
            request = user_pb2.CheckFollowingRequest(
                user_id=user_id,
                following_id=following_id
            )
            return self.stub.CheckFollowingStatus(request)
        except grpc.RpcError as e:
            log_msg("error", f"gRPC error in check_following_status: {str(e)}")
            raise e

class CommentsServiceClient:
    def __init__(self, host='localhost', port=50053):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = comments_pb2_grpc.CommentsServiceStub(self.channel)

    def create_comment(self, post_id: str, user_id: str, content: str, parent_comment_id: str = None):
        request = comments_pb2.CommentCreateRequest(
            post_id=post_id,
            user_id=user_id,
            content=content,
            parent_comment_id=parent_comment_id if parent_comment_id else ""
        )
        return self.stub.CreateComment(request)

    def get_comment(self, comment_id: str):
        request = comments_pb2.CommentRequest(comment_id=comment_id)
        return self.stub.GetComment(request)

    def get_comments_by_post(self, post_id: str):
        request = comments_pb2.PostCommentsRequest(post_id=post_id)
        return self.stub.GetCommentsByPost(request)

    def get_replies(self, comment_id: str):
        request = comments_pb2.CommentRequest(comment_id=comment_id)
        return self.stub.GetReplies(request)

    def update_comment(self, comment_id: str, content: str):
        request = comments_pb2.CommentUpdateRequest(
            comment_id=comment_id,
            content=content
        )
        return self.stub.UpdateComment(request)

    def delete_comment(self, comment_id: str):
        request = comments_pb2.CommentRequest(comment_id=comment_id)
        return self.stub.DeleteComment(request)

    def like_comment(self, comment_id: str, user_id: str):
        request = comments_pb2.LikeCommentRequest(
            comment_id=comment_id,
            user_id=user_id
        )
        return self.stub.LikeComment(request)

    def unlike_comment(self, comment_id: str, user_id: str):
        request = comments_pb2.UnlikeCommentRequest(
            comment_id=comment_id,
            user_id=user_id
        )
        return self.stub.UnlikeComment(request)

class PostsServiceClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50053')
        self.stub = post_pb2_grpc.PostsServiceStub(self.channel)

    def search_posts(self, property_type: str = None, location: str = None,
                    min_price: float = None, max_price: float = None,
                    status: str = None, page: int = 1, limit: int = 10):
        try:
            request = post_pb2.SearchPostsRequest(
                property_type=property_type or "",
                location=location or "",
                min_price=min_price or 0.0,
                max_price=max_price or 0.0,
                status=status or "",
                page=page,
                limit=limit
            )
            return self.stub.SearchPosts(request)
        except grpc.RpcError as e:
            print(f"Error in search_posts: {str(e)}")
            return None

    def create_post(self, user_id: int, title: str, content: str,
                   visibility: str, property_type: str, location: str,
                   map_location: str, price: float, status: str,
                   media: list = None) -> dict:
        try:
            media_list = []
            if media:
                for m in media:
                    try:
                        media_data = base64.b64decode(m.mediaData)
                    except Exception as e:
                        return {
                            'success': False,
                            'message': f'Invalid media data format: {str(e)}'
                        }

                    media_upload = post_pb2.PostMediaUpload(
                        media_type=m.mediaType,
                        media_data=media_data,
                        media_order=m.mediaOrder,
                        caption=m.caption
                    )
                    media_list.append(media_upload)

            request = post_pb2.PostCreateRequest(
                user_id=user_id,
                title=title,
                content=content,
                visibility=visibility,
                property_type=property_type,
                location=location,
                map_location=map_location,
                price=price,
                status=status,
                media=media_list
            )
            response = self.stub.CreatePost(request)
            
            # Convert the gRPC response to a dictionary
            if response.post:
                media_list = []
                for m in response.post.media:
                    media_list.append({
                        'id': m.id,
                        'mediaType': m.media_type,
                        'mediaUrl': m.media_url,
                        'mediaOrder': m.media_order,
                        'mediaSize': m.media_size,
                        'caption': m.caption,
                        'uploadedAt': datetime.fromtimestamp(m.uploaded_at)
                    })

                post_dict = {
                    'id': response.post.id,
                    'userId': response.post.user_id,
                    'title': response.post.title,
                    'content': response.post.content,
                    'visibility': response.post.visibility,
                    'propertyType': response.post.property_type,
                    'location': response.post.location,
                    'mapLocation': response.post.map_location,
                    'price': response.post.price,
                    'status': response.post.status,
                    'createdAt': datetime.fromtimestamp(response.post.created_at),
                    'media': media_list,
                    'likeCount': response.post.like_count,
                    'commentCount': response.post.comment_count
                }
            else:
                post_dict = None

            return {
                'success': response.success,
                'message': response.message,
                'post': post_dict
            }
        except grpc.RpcError as e:
            return {
                'success': False,
                'message': f'Error creating post: {str(e)}',
                'post': None
            }

    def get_post(self, post_id: int):
        try:
            request = post_pb2.PostRequest(post_id=post_id)
            return self.stub.GetPost(request)
        except grpc.RpcError as e:
            return None

    def update_post(self, post_id: int, **kwargs) -> dict:
        try:
            # Filter out None values
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            # Convert camelCase to snake_case for property_type and map_location
            if 'propertyType' in update_data:
                update_data['property_type'] = update_data.pop('propertyType')
            if 'mapLocation' in update_data:
                update_data['map_location'] = update_data.pop('mapLocation')

            request = post_pb2.PostUpdateRequest(
                post_id=post_id,
                **update_data
            )
            response = self.stub.UpdatePost(request)
            
            # Convert the gRPC response to a dictionary
            if response.post:
                media_list = []
                for m in response.post.media:
                    media_list.append({
                        'id': m.id,
                        'mediaType': m.media_type,
                        'mediaUrl': m.media_url,
                        'mediaOrder': m.media_order,
                        'mediaSize': m.media_size,
                        'caption': m.caption,
                        'uploadedAt': datetime.fromtimestamp(m.uploaded_at)
                    })

                post_dict = {
                    'id': response.post.id,
                    'userId': response.post.user_id,
                    'title': response.post.title,
                    'content': response.post.content,
                    'visibility': response.post.visibility,
                    'propertyType': response.post.property_type,
                    'location': response.post.location,
                    'mapLocation': response.post.map_location,
                    'price': response.post.price,
                    'status': response.post.status,
                    'createdAt': datetime.fromtimestamp(response.post.created_at),
                    'media': media_list,
                    'likeCount': response.post.like_count,
                    'commentCount': response.post.comment_count
                }
            else:
                post_dict = None

            return {
                'success': response.success,
                'message': response.message,
                'post': post_dict
            }
        except grpc.RpcError as e:
            return {
                'success': False,
                'message': f'Error updating post: {str(e)}',
                'post': None
            }

    def delete_post(self, post_id: int):
        try:
            request = post_pb2.PostRequest(post_id=post_id)
            response = self.stub.DeletePost(request)
            return {
                'success': True,
                'message': 'Post deleted successfully'
            }
        except grpc.RpcError as e:
            return {
                'success': False,
                'message': f'Error deleting post: {str(e)}'
            }

    def get_posts_by_user(self, user_id: int, page: int = 1, limit: int = 10):
        try:
            request = post_pb2.GetPostsByUserRequest(
                user_id=user_id,
                page=page,
                limit=limit
            )
            response = self.stub.GetPostsByUser(request)
            return response.posts
        except grpc.RpcError as e:
            return []

    def like_post(self, post_id: int, user_id: int) -> dict:
        try:
            # First check if the post exists
            post_request = post_pb2.PostRequest(post_id=post_id)
            post_response = self.stub.GetPost(post_request)
            if not post_response.post:
                return {
                    'success': False,
                    'message': f'Post with ID {post_id} not found',
                    'post': None
                }

            request = post_pb2.LikeRequest(
                post_id=post_id,  # Changed from id to post_id
                user_id=user_id,
                reaction_type='like'
            )
            response = self.stub.LikePost(request)
            
            # Convert the gRPC response to a dictionary
            if response.post:
                media_list = []
                for m in response.post.media:
                    media_list.append({
                        'id': m.id,
                        'mediaType': m.media_type,
                        'mediaUrl': m.media_url,
                        'mediaOrder': m.media_order,
                        'mediaSize': m.media_size,
                        'caption': m.caption,
                        'uploadedAt': datetime.fromtimestamp(m.uploaded_at)
                    })

                post_dict = {
                    'id': response.post.id,
                    'userId': response.post.user_id,
                    'title': response.post.title,
                    'content': response.post.content,
                    'visibility': response.post.visibility,
                    'propertyType': response.post.property_type,
                    'location': response.post.location,
                    'mapLocation': response.post.map_location,
                    'price': response.post.price,
                    'status': response.post.status,
                    'createdAt': datetime.fromtimestamp(response.post.created_at),
                    'media': media_list,
                    'likeCount': response.post.like_count,
                    'commentCount': response.post.comment_count
                }
            else:
                post_dict = None

            return {
                'success': response.success,
                'message': response.message,
                'post': post_dict
            }
        except grpc.RpcError as e:
            return {
                'success': False,
                'message': f'Error liking post: {str(e)}',
                'post': None
            }

    def unlike_post(self, post_id: int, user_id: int) -> dict:
        try:
            request = post_pb2.LikeRequest(
                post_id=post_id,  # Changed from id to post_id
                user_id=user_id
            )
            response = self.stub.UnlikePost(request)
            
            # Convert the gRPC response to a dictionary
            if response.post:
                media_list = []
                for m in response.post.media:
                    media_list.append({
                        'id': m.id,
                        'mediaType': m.media_type,
                        'mediaUrl': m.media_url,
                        'mediaOrder': m.media_order,
                        'mediaSize': m.media_size,
                        'caption': m.caption,
                        'uploadedAt': datetime.fromtimestamp(m.uploaded_at)
                    })

                post_dict = {
                    'id': response.post.id,
                    'userId': response.post.user_id,
                    'title': response.post.title,
                    'content': response.post.content,
                    'visibility': response.post.visibility,
                    'propertyType': response.post.property_type,
                    'location': response.post.location,
                    'mapLocation': response.post.map_location,
                    'price': response.post.price,
                    'status': response.post.status,
                    'createdAt': datetime.fromtimestamp(response.post.created_at),
                    'media': media_list,
                    'likeCount': response.post.like_count,
                    'commentCount': response.post.comment_count
                }
            else:
                post_dict = None

            return {
                'success': response.success,
                'message': response.message,
                'post': post_dict
            }
        except grpc.RpcError as e:
            return {
                'success': False,
                'message': f'Error unliking post: {str(e)}',
                'post': None
            }

    def delete_post_media(self, media_id: int) -> dict:
        try:
            request = post_pb2.PostRequest(post_id=media_id)
            response = self.stub.DeletePostMedia(request)
            
            return {
                'success': response.success,
                'message': response.message
            }
        except grpc.RpcError as e:
            return {
                'success': False,
                'message': f'Error deleting media: {str(e)}'
            }

    def add_post_media(self, post_id: int, media: list) -> dict:
        try:
            media_list = []
            for m in media:
                try:
                    media_data = base64.b64decode(m.mediaData)
                except Exception as e:
                    return {
                        'success': False,
                        'message': f'Invalid media data format: {str(e)}'
                    }

                media_upload = post_pb2.PostMediaUpload(
                    media_type=m.mediaType,
                    media_data=media_data,
                    media_order=m.mediaOrder,
                    caption=m.caption
                )
                media_list.append(media_upload)

            request = post_pb2.PostMediaRequest(
                post_id=post_id,
                media=media_list
            )
            response = self.stub.AddPostMedia(request)
            
            # Convert the gRPC response to a dictionary
            if response.post:
                media_list = []
                for m in response.post.media:
                    media_list.append({
                        'id': m.id,
                        'mediaType': m.media_type,
                        'mediaUrl': m.media_url,
                        'mediaOrder': m.media_order,
                        'mediaSize': m.media_size,
                        'caption': m.caption,
                        'uploadedAt': datetime.fromtimestamp(m.uploaded_at)
                    })

                post_dict = {
                    'id': response.post.id,
                    'userId': response.post.user_id,
                    'title': response.post.title,
                    'content': response.post.content,
                    'visibility': response.post.visibility,
                    'propertyType': response.post.property_type,
                    'location': response.post.location,
                    'mapLocation': response.post.map_location,
                    'price': response.post.price,
                    'status': response.post.status,
                    'createdAt': datetime.fromtimestamp(response.post.created_at),
                    'media': media_list,
                    'likeCount': response.post.like_count,
                    'commentCount': response.post.comment_count
                }
            else:
                post_dict = None

            return {
                'success': response.success,
                'message': response.message,
                'post': post_dict
            }
        except grpc.RpcError as e:
            return {
                'success': False,
                'message': f'Error adding media: {str(e)}',
                'post': None
            }

    def create_comment(self, post_id: int, user_id: int, comment: str,
                      parent_comment_id: Optional[int] = None) -> dict:
        try:
            request = post_pb2.CommentCreateRequest(
                post_id=post_id,
                user_id=user_id,
                comment=comment,
                parent_comment_id=parent_comment_id or 0
            )
            response = self.stub.CreateComment(request)
            
            # Convert the gRPC response to a dictionary
            if response:
                comment_dict = {
                    'id': response.id,
                    'postId': response.post_id,
                    'userId': response.user_id,
                    'comment': response.comment,
                    'parentCommentId': response.parent_comment_id if response.parent_comment_id != 0 else None,
                    'status': response.status,
                    'addedAt': datetime.fromtimestamp(response.added_at),
                    'commentedAt': datetime.fromtimestamp(response.commented_at),
                    'replies': [],  # Replies will be fetched separately if needed
                    'likeCount': response.like_count
                }
            else:
                comment_dict = None

            return {
                'success': True,
                'message': 'Comment created successfully',
                'comment': comment_dict
            }
        except grpc.RpcError as e:
            return {
                'success': False,
                'message': f'Error creating comment: {str(e)}',
                'comment': None
            }

    def update_comment(self, comment_id: int, comment: Optional[str] = None,
                      status: Optional[str] = None) -> dict:
        try:
            request = post_pb2.CommentUpdateRequest(
                comment_id=comment_id,
                comment=comment,
                status=status
            )
            response = self.stub.UpdateComment(request)
            
            # Convert the gRPC response to a dictionary
            if response:
                comment_dict = {
                    'id': response.id,
                    'postId': response.post_id,
                    'userId': response.user_id,
                    'comment': response.comment,
                    'parentCommentId': response.parent_comment_id if response.parent_comment_id != 0 else None,
                    'status': response.status,
                    'addedAt': datetime.fromtimestamp(response.added_at),
                    'commentedAt': datetime.fromtimestamp(response.commented_at),
                    'replies': [],  # Replies will be fetched separately if needed
                    'likeCount': response.like_count
                }
            else:
                comment_dict = None

            return {
                'success': True,
                'message': 'Comment updated successfully',
                'comment': comment_dict
            }
        except grpc.RpcError as e:
            return {
                'success': False,
                'message': f'Error updating comment: {str(e)}',
                'comment': None
            }

    def delete_comment(self, comment_id: int) -> dict:
        try:
            request = post_pb2.PostRequest(post_id=comment_id)  # Using PostRequest for comment_id
            response = self.stub.DeleteComment(request)
            return {
                'success': True,
                'message': 'Comment deleted successfully',
                'comment': None
            }
        except grpc.RpcError as e:
            return {
                'success': False,
                'message': f'Error deleting comment: {str(e)}',
                'comment': None
            }

    def like_comment(self, comment_id: int, user_id: int) -> dict:
        try:
            request = post_pb2.CommentLikeRequest(
                comment_id=comment_id,
                user_id=user_id,
                reaction_type='like'
            )
            response = self.stub.LikeComment(request)
            
            # Convert the gRPC response to a dictionary
            if response.comment:
                comment_dict = {
                    'id': response.comment.id,
                    'postId': response.comment.post_id,
                    'userId': response.comment.user_id,
                    'comment': response.comment.comment,
                    'parentCommentId': response.comment.parent_comment_id if response.comment.parent_comment_id != 0 else None,
                    'status': response.comment.status,
                    'addedAt': datetime.fromtimestamp(response.comment.added_at),
                    'commentedAt': datetime.fromtimestamp(response.comment.commented_at),
                    'replies': [],  # Replies will be fetched separately if needed
                    'likeCount': response.comment.like_count
                }
            else:
                comment_dict = None

            return {
                'success': response.success,
                'message': response.message,
                'comment': comment_dict
            }
        except grpc.RpcError as e:
            return {
                'success': False,
                'message': f'Error liking comment: {str(e)}',
                'comment': None
            }

    def unlike_comment(self, comment_id: int, user_id: int) -> dict:
        try:
            request = post_pb2.CommentLikeRequest(
                comment_id=comment_id,
                user_id=user_id
            )
            response = self.stub.UnlikeComment(request)
            
            # Convert the gRPC response to a dictionary
            if response.comment:
                comment_dict = {
                    'id': response.comment.id,
                    'postId': response.comment.post_id,
                    'userId': response.comment.user_id,
                    'comment': response.comment.comment,
                    'parentCommentId': response.comment.parent_comment_id if response.comment.parent_comment_id != 0 else None,
                    'status': response.comment.status,
                    'addedAt': datetime.fromtimestamp(response.comment.added_at),
                    'commentedAt': datetime.fromtimestamp(response.comment.commented_at),
                    'replies': [],  # Replies will be fetched separately if needed
                    'likeCount': response.comment.like_count
                }
            else:
                comment_dict = None

            return {
                'success': response.success,
                'message': response.message,
                'comment': comment_dict
            }
        except grpc.RpcError as e:
            return {
                'success': False,
                'message': f'Error unliking comment: {str(e)}',
                'comment': None
            }

class PropertyServiceClient:
    def __init__(self, host='localhost', port=50053):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = property_pb2_grpc.PropertyServiceStub(self.channel)

    def create_property(self, **property_data):
        request = property_pb2.Property(**property_data)
        return self.stub.CreateProperty(request)

    def get_property(self, property_id: str):
        request = property_pb2.PropertyRequest(property_id=property_id)
        return self.stub.GetProperty(request)

    def update_property(self, property_id: str, **property_data):
        property_data['property_id'] = property_id
        request = property_pb2.Property(**property_data)
        return self.stub.UpdateProperty(request)

    def delete_property(self, property_id: str):
        request = property_pb2.PropertyRequest(property_id=property_id)
        return self.stub.DeleteProperty(request)

    def search_properties(self, **search_params):
        request = property_pb2.PropertySearchRequest(**search_params)
        return self.stub.SearchProperties(request)

    def list_properties(self):
        request = property_pb2.PropertyRequest()
        return self.stub.ListProperties(request)

    def increment_view_count(self, property_id: str):
        request = property_pb2.PropertyRequest(property_id=property_id)
        return self.stub.IncrementViewCount(request)

    def search_posts(self, property_type: str = None, location: str = None,
                    min_price: float = None, max_price: float = None,
                    status: str = None, page: int = 1, limit: int = 10) -> list:
        try:
            request = post_pb2.SearchPostsRequest(
                property_type=property_type or "",
                location=location or "",
                min_price=min_price or 0.0,
                max_price=max_price or 0.0,
                status=status or "",
                page=page,
                limit=limit
            )
            response = self.stub.SearchPosts(request)
            
            # Convert the gRPC response to a list of dictionaries
            posts = []
            for post in response.posts:
                media_list = []
                for m in post.media:
                    media_list.append({
                        'id': m.id,
                        'mediaType': m.media_type,
                        'mediaUrl': m.media_url,
                        'mediaOrder': m.media_order,
                        'mediaSize': m.media_size,
                        'caption': m.caption,
                        'uploadedAt': datetime.fromtimestamp(m.uploaded_at)
                    })

                posts.append({
                    'id': post.id,
                    'userId': post.user_id,
                    'title': post.title,
                    'content': post.content,
                    'visibility': post.visibility,
                    'propertyType': post.property_type,
                    'location': post.location,
                    'mapLocation': post.map_location,
                    'price': post.price,
                    'status': post.status,
                    'createdAt': datetime.fromtimestamp(post.created_at),
                    'media': media_list,
                    'likeCount': post.like_count,
                    'commentCount': post.comment_count
                })
            return posts
        except grpc.RpcError as e:
            return []

    def get_comments(self, post_id: int, page: int = 1, limit: int = 10) -> list:
        try:
            request = post_pb2.GetCommentsRequest(
                post_id=post_id,
                page=page,
                limit=limit
            )
            response = self.stub.GetComments(request)
            
            # Convert the gRPC response to a list of dictionaries
            comments = []
            for comment in response.comments:
                comments.append({
                    'id': comment.id,
                    'postId': comment.post_id,
                    'userId': comment.user_id,
                    'comment': comment.comment,
                    'parentCommentId': comment.parent_comment_id if comment.parent_comment_id != 0 else None,
                    'status': comment.status,
                    'addedAt': datetime.fromtimestamp(comment.added_at),
                    'commentedAt': datetime.fromtimestamp(comment.commented_at),
                    'replies': [],  # Replies will be handled separately
                    'likeCount': comment.like_count
                })
            return comments
        except grpc.RpcError as e:
            return []

    def add_post_media(self, post_id: int, media: list) -> dict:
        try:
            media_list = []
            for m in media:
                # Convert base64 string to bytes
                try:
                    media_data = base64.b64decode(m.mediaData)
                except Exception as e:
                    return {
                        'success': False,
                        'message': f'Invalid media data format: {str(e)}'
                    }

                media_upload = post_pb2.PostMediaUpload(
                    media_type=m.mediaType,
                    media_data=media_data,
                    media_order=m.mediaOrder,
                    caption=m.caption
                )
                media_list.append(media_upload)

            request = post_pb2.PostMediaRequest(
                post_id=post_id,
                media=media_list
            )
            response = self.stub.AddPostMedia(request)
            
            # Convert the gRPC response to a dictionary
            if response.post:
                media_list = []
                for m in response.post.media:
                    media_list.append({
                        'id': m.id,
                        'mediaType': m.media_type,
                        'mediaUrl': m.media_url,
                        'mediaOrder': m.media_order,
                        'mediaSize': m.media_size,
                        'caption': m.caption,
                        'uploadedAt': datetime.fromtimestamp(m.uploaded_at)
                    })

                post_dict = {
                    'id': response.post.id,
                    'userId': response.post.user_id,
                    'title': response.post.title,
                    'content': response.post.content,
                    'visibility': response.post.visibility,
                    'propertyType': response.post.property_type,
                    'location': response.post.location,
                    'mapLocation': response.post.map_location,
                    'price': response.post.price,
                    'status': response.post.status,
                    'createdAt': datetime.fromtimestamp(response.post.created_at),
                    'media': media_list,
                    'likeCount': response.post.like_count,
                    'commentCount': response.post.comment_count
                }
            else:
                post_dict = None

            return {
                'success': response.success,
                'message': response.message,
                'post': post_dict
            }
        except grpc.RpcError as e:
            return {
                'success': False,
                'message': f'Error adding media: {str(e)}',
                'post': None
            }

    def delete_post_media(self, media_id: int) -> dict:
        try:
            request = post_pb2.PostRequest(post_id=media_id)
            response = self.stub.DeletePostMedia(request)
            
            return {
                'success': response.success,
                'message': response.message
            }
        except grpc.RpcError as e:
            return {
                'success': False,
                'message': f'Error deleting media: {str(e)}'
            }

# Create singleton instances
auth_client = AuthServiceClient()
user_client = UserServiceClient()
comments_client = CommentsServiceClient()
posts_client = PostsServiceClient()
property_client = PropertyServiceClient()

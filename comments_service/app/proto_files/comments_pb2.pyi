from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Comment(_message.Message):
    __slots__ = ("comment_id", "post_id", "user_id", "content", "parent_comment_id", "created_at", "updated_at", "like_count")
    COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    PARENT_COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    LIKE_COUNT_FIELD_NUMBER: _ClassVar[int]
    comment_id: str
    post_id: str
    user_id: str
    content: str
    parent_comment_id: str
    created_at: int
    updated_at: int
    like_count: int
    def __init__(self, comment_id: _Optional[str] = ..., post_id: _Optional[str] = ..., user_id: _Optional[str] = ..., content: _Optional[str] = ..., parent_comment_id: _Optional[str] = ..., created_at: _Optional[int] = ..., updated_at: _Optional[int] = ..., like_count: _Optional[int] = ...) -> None: ...

class CommentList(_message.Message):
    __slots__ = ("comments",)
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    comments: _containers.RepeatedCompositeFieldContainer[Comment]
    def __init__(self, comments: _Optional[_Iterable[_Union[Comment, _Mapping]]] = ...) -> None: ...

class CommentRequest(_message.Message):
    __slots__ = ("comment_id",)
    COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    comment_id: str
    def __init__(self, comment_id: _Optional[str] = ...) -> None: ...

class PostCommentsRequest(_message.Message):
    __slots__ = ("post_id",)
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    def __init__(self, post_id: _Optional[str] = ...) -> None: ...

class CommentCreateRequest(_message.Message):
    __slots__ = ("post_id", "user_id", "content", "parent_comment_id")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    PARENT_COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    user_id: str
    content: str
    parent_comment_id: str
    def __init__(self, post_id: _Optional[str] = ..., user_id: _Optional[str] = ..., content: _Optional[str] = ..., parent_comment_id: _Optional[str] = ...) -> None: ...

class CommentUpdateRequest(_message.Message):
    __slots__ = ("comment_id", "content")
    COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    comment_id: str
    content: str
    def __init__(self, comment_id: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class LikeCommentRequest(_message.Message):
    __slots__ = ("comment_id", "user_id")
    COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    comment_id: str
    user_id: str
    def __init__(self, comment_id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class CommentResponse(_message.Message):
    __slots__ = ("success", "message", "comment")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    comment: Comment
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., comment: _Optional[_Union[Comment, _Mapping]] = ...) -> None: ...

class CommentListResponse(_message.Message):
    __slots__ = ("success", "message", "comments")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    comments: CommentList
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., comments: _Optional[_Union[CommentList, _Mapping]] = ...) -> None: ...

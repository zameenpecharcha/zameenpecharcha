# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: post.proto
# Protobuf Python Version: 6.31.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    31,
    0,
    '',
    'post.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\npost.proto\x12\x05posts\"\x9b\x01\n\x04Post\x12\x0f\n\x07post_id\x18\x01 \x01(\t\x12\x0f\n\x07user_id\x18\x02 \x01(\t\x12\r\n\x05title\x18\x03 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x04 \x01(\t\x12\x12\n\ncreated_at\x18\x05 \x01(\x03\x12\x12\n\nupdated_at\x18\x06 \x01(\x03\x12\x12\n\nlike_count\x18\x07 \x01(\x05\x12\x15\n\rcomment_count\x18\x08 \x01(\x05\"&\n\x08PostList\x12\x1a\n\x05posts\x18\x01 \x03(\x0b\x32\x0b.posts.Post\"\x1e\n\x0bPostRequest\x12\x0f\n\x07post_id\x18\x01 \x01(\t\"D\n\x11PostCreateRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t\"D\n\x11PostUpdateRequest\x12\x0f\n\x07post_id\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t\"3\n\x0fLikePostRequest\x12\x0f\n\x07post_id\x18\x01 \x01(\t\x12\x0f\n\x07user_id\x18\x02 \x01(\t\"(\n\x15GetPostsByUserRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\"K\n\x0cPostResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x19\n\x04post\x18\x03 \x01(\x0b\x32\x0b.posts.Post\"T\n\x10PostListResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x1e\n\x05posts\x18\x03 \x01(\x0b\x32\x0f.posts.PostList2\xbe\x03\n\x0cPostsService\x12=\n\nCreatePost\x12\x18.posts.PostCreateRequest\x1a\x13.posts.PostResponse\"\x00\x12\x34\n\x07GetPost\x12\x12.posts.PostRequest\x1a\x13.posts.PostResponse\"\x00\x12=\n\nUpdatePost\x12\x18.posts.PostUpdateRequest\x1a\x13.posts.PostResponse\"\x00\x12\x37\n\nDeletePost\x12\x12.posts.PostRequest\x1a\x13.posts.PostResponse\"\x00\x12I\n\x0eGetPostsByUser\x12\x1c.posts.GetPostsByUserRequest\x1a\x17.posts.PostListResponse\"\x00\x12\x39\n\x08LikePost\x12\x16.posts.LikePostRequest\x1a\x13.posts.PostResponse\"\x00\x12;\n\nUnlikePost\x12\x16.posts.LikePostRequest\x1a\x13.posts.PostResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'post_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_POST']._serialized_start=22
  _globals['_POST']._serialized_end=177
  _globals['_POSTLIST']._serialized_start=179
  _globals['_POSTLIST']._serialized_end=217
  _globals['_POSTREQUEST']._serialized_start=219
  _globals['_POSTREQUEST']._serialized_end=249
  _globals['_POSTCREATEREQUEST']._serialized_start=251
  _globals['_POSTCREATEREQUEST']._serialized_end=319
  _globals['_POSTUPDATEREQUEST']._serialized_start=321
  _globals['_POSTUPDATEREQUEST']._serialized_end=389
  _globals['_LIKEPOSTREQUEST']._serialized_start=391
  _globals['_LIKEPOSTREQUEST']._serialized_end=442
  _globals['_GETPOSTSBYUSERREQUEST']._serialized_start=444
  _globals['_GETPOSTSBYUSERREQUEST']._serialized_end=484
  _globals['_POSTRESPONSE']._serialized_start=486
  _globals['_POSTRESPONSE']._serialized_end=561
  _globals['_POSTLISTRESPONSE']._serialized_start=563
  _globals['_POSTLISTRESPONSE']._serialized_end=647
  _globals['_POSTSSERVICE']._serialized_start=650
  _globals['_POSTSSERVICE']._serialized_end=1096
# @@protoc_insertion_point(module_scope)

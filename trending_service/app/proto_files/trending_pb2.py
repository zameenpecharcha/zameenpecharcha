# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: trending.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0etrending.proto\x12\x08trending\"p\n\x0cTrendingPost\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0f\n\x07post_id\x18\x02 \x01(\x05\x12\r\n\x05score\x18\x03 \x01(\x02\x12\x0c\n\x04rank\x18\x04 \x01(\x05\x12\x12\n\ncreated_at\x18\x05 \x01(\t\x12\x12\n\nupdated_at\x18\x06 \x01(\t\"B\n\x10TrendingPostList\x12.\n\x0etrending_posts\x18\x01 \x03(\x0b\x32\x16.trending.TrendingPost\"V\n\x18UpdatePostMetricsRequest\x12\x0f\n\x07post_id\x18\x01 \x01(\x05\x12\x12\n\nlike_count\x18\x02 \x01(\x05\x12\x15\n\rcomment_count\x18\x03 \x01(\x05\"3\n\x12GetTrendingRequest\x12\r\n\x05limit\x18\x01 \x01(\x05\x12\x0e\n\x06offset\x18\x02 \x01(\x05\"%\n\x12GetPostRankRequest\x12\x0f\n\x07post_id\x18\x01 \x01(\x05\"c\n\x10TrendingResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12-\n\rtrending_post\x18\x03 \x01(\x0b\x32\x16.trending.TrendingPost\"k\n\x13GetTrendingResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x32\n\x0etrending_posts\x18\x03 \x01(\x0b\x32\x1a.trending.TrendingPostList\">\n\x0cRankResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x0c\n\x04rank\x18\x03 \x01(\x05\x32\x82\x02\n\x0fTrendingService\x12U\n\x11UpdatePostMetrics\x12\".trending.UpdatePostMetricsRequest\x1a\x1a.trending.TrendingResponse\"\x00\x12Q\n\x10GetTrendingPosts\x12\x1c.trending.GetTrendingRequest\x1a\x1d.trending.GetTrendingResponse\"\x00\x12\x45\n\x0bGetPostRank\x12\x1c.trending.GetPostRankRequest\x1a\x16.trending.RankResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'trending_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_TRENDINGPOST']._serialized_start=28
  _globals['_TRENDINGPOST']._serialized_end=140
  _globals['_TRENDINGPOSTLIST']._serialized_start=142
  _globals['_TRENDINGPOSTLIST']._serialized_end=208
  _globals['_UPDATEPOSTMETRICSREQUEST']._serialized_start=210
  _globals['_UPDATEPOSTMETRICSREQUEST']._serialized_end=296
  _globals['_GETTRENDINGREQUEST']._serialized_start=298
  _globals['_GETTRENDINGREQUEST']._serialized_end=349
  _globals['_GETPOSTRANKREQUEST']._serialized_start=351
  _globals['_GETPOSTRANKREQUEST']._serialized_end=388
  _globals['_TRENDINGRESPONSE']._serialized_start=390
  _globals['_TRENDINGRESPONSE']._serialized_end=489
  _globals['_GETTRENDINGRESPONSE']._serialized_start=491
  _globals['_GETTRENDINGRESPONSE']._serialized_end=598
  _globals['_RANKRESPONSE']._serialized_start=600
  _globals['_RANKRESPONSE']._serialized_end=662
  _globals['_TRENDINGSERVICE']._serialized_start=665
  _globals['_TRENDINGSERVICE']._serialized_end=923
# @@protoc_insertion_point(module_scope)

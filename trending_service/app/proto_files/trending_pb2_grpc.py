"""Generated protocol buffer code."""
import grpc

from app.proto_files import trending_pb2 as trending__pb2

class TrendingServiceStub(object):
    """Search Service Definition
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.UpdatePostMetrics = channel.unary_unary(
                '/trending.TrendingService/UpdatePostMetrics',
                request_serializer=trending__pb2.UpdatePostMetricsRequest.SerializeToString,
                response_deserializer=trending__pb2.TrendingResponse.FromString,
                )
        self.GetTrendingPosts = channel.unary_unary(
                '/trending.TrendingService/GetTrendingPosts',
                request_serializer=trending__pb2.GetTrendingRequest.SerializeToString,
                response_deserializer=trending__pb2.GetTrendingResponse.FromString,
                )
        self.GetPostRank = channel.unary_unary(
                '/trending.TrendingService/GetPostRank',
                request_serializer=trending__pb2.GetPostRankRequest.SerializeToString,
                response_deserializer=trending__pb2.RankResponse.FromString,
                )

class TrendingServiceServicer(object):
    """Search Service Definition
    """

    def UpdatePostMetrics(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetTrendingPosts(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPostRank(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_TrendingServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'UpdatePostMetrics': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdatePostMetrics,
                    request_deserializer=trending__pb2.UpdatePostMetricsRequest.FromString,
                    response_serializer=trending__pb2.TrendingResponse.SerializeToString,
            ),
            'GetTrendingPosts': grpc.unary_unary_rpc_method_handler(
                    servicer.GetTrendingPosts,
                    request_deserializer=trending__pb2.GetTrendingRequest.FromString,
                    response_serializer=trending__pb2.GetTrendingResponse.SerializeToString,
            ),
            'GetPostRank': grpc.unary_unary_rpc_method_handler(
                    servicer.GetPostRank,
                    request_deserializer=trending__pb2.GetPostRankRequest.FromString,
                    response_serializer=trending__pb2.RankResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'trending.TrendingService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class TrendingService(object):
    """Trending Service Definition
    """

    @staticmethod
    def UpdatePostMetrics(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/trending.TrendingService/UpdatePostMetrics',
            trending__pb2.UpdatePostMetricsRequest.SerializeToString,
            trending__pb2.TrendingResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetTrendingPosts(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/trending.TrendingService/GetTrendingPosts',
            trending__pb2.GetTrendingRequest.SerializeToString,
            trending__pb2.GetTrendingResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetPostRank(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/trending.TrendingService/GetPostRank',
            trending__pb2.GetPostRankRequest.SerializeToString,
            trending__pb2.RankResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

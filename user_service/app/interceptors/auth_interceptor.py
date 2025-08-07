import grpc
from app.utils.log_utils import log_msg
from app.utils.jwt_utils import verify_jwt_token

class AuthServerInterceptor(grpc.ServerInterceptor):
    # List of methods that don't require authentication
    PUBLIC_METHODS = [
        '/user.UserService/CreateUser',  # User registration endpoint
    ]

    def intercept_service(self, continuation, handler_call_details):
        # Check if the method is public
        if handler_call_details.method in self.PUBLIC_METHODS:
            return continuation(handler_call_details)

        # For protected endpoints, verify authentication
        metadata = dict(handler_call_details.invocation_metadata)
        token = metadata.get("authorization", "").replace("Bearer ", "")

        if not token:
            def deny_handler(request, context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing token")
            return grpc.unary_unary_rpc_method_handler(deny_handler)

        try:
            payload, error = verify_jwt_token(token)
            if error:
                def deny_handler(request, context):
                    context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid token")
                return grpc.unary_unary_rpc_method_handler(deny_handler)

            # Token is valid, proceed with the request
            return continuation(handler_call_details)

        except Exception as e:
            log_msg("error", f"Interceptor token validation failed: {str(e)}")

            def deny_handler(request, context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token validation failed")

            return grpc.unary_unary_rpc_method_handler(deny_handler)
import json
import re
import grpc

from starlette.types import ASGIApp, Receive, Scope, Send
from fastapi import Request
from starlette.responses import JSONResponse
from app.clients.auth.auth_client import auth_service_client
from app.utils.log_utils import log_msg

# Public GraphQL operation names (matched case-insensitively)
# Add any operation here to bypass the auth middleware
PUBLIC_GRAPHQL_OPS = {
    "login",
    "sendotp",
    "verifyotp",
    "forgotpassword",
    "resetpassword",
    "createuser",
    "logout",
}

class AuthMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Read full body to inspect GraphQL operation
        body = b""
        more_body = True
        while more_body:
            message = await receive()
            if message["type"] == "http.request":
                body += message.get("body", b"")
                more_body = message.get("more_body", False)

        async def receive_with_body():
            return {"type": "http.request", "body": body, "more_body": False}

        request = Request(scope, receive=receive_with_body)

        # Always allow OPTIONS requests for CORS
        if request.method == "OPTIONS":
            await self.app(scope, receive_with_body, send)
            return

        if self._should_skip_auth(request, body):
            await self.app(scope, receive_with_body, send)
            return

        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise ValueError("Missing or invalid Authorization header")

            token = auth_header.split(" ")[1]
            response = auth_service_client.validate_token(token)

            if not response.valid:
                raise ValueError(response.message or "Invalid or expired token")

            # Propagate user to downstream handlers
            request.state.user = {
                "id": response.user_info.id,
                "email": response.user_info.email,
                "role": response.user_info.role,
                "first_name": response.user_info.first_name,
                "last_name": response.user_info.last_name,
            }
            scope["state"] = request.state._state

            await self.app(scope, receive_with_body, send)

        except ValueError as e:
            log_msg("warn", f"Authentication failed: {str(e)}")
            res = JSONResponse(
                status_code=401,
                content={"detail": str(e)},
                headers={"Access-Control-Allow-Origin": "*"}
            )
            await res(scope, receive_with_body, send)

        except grpc.RpcError as e:
            log_msg("error", f"gRPC error: {str(e)}")
            status = 401 if e.code() == grpc.StatusCode.UNAUTHENTICATED else 403
            detail = e.details() or "Authorization failed"
            res = JSONResponse(
                status_code=status,
                content={"detail": detail},
                headers={"Access-Control-Allow-Origin": "*"}
            )
            await res(scope, receive_with_body, send)

        except Exception as e:
            log_msg("error", f"AuthMiddleware error: {str(e)}")
            res = JSONResponse(
                status_code=500,
                content={"detail": str(e)},
                headers={"Access-Control-Allow-Origin": "*"}
            )
            await res(scope, receive_with_body, send)

    def _should_skip_auth(self, request: Request, body: bytes) -> bool:
        path = request.url.path

        if any(path.startswith(p) for p in ["/health", "/docs", "/redoc", "/openapi.json"]):
            return True

        if path.startswith("/api/v1/graphql"):
            try:
                parsed = json.loads(body.decode("utf-8"))
                query = parsed.get("query", "")
                # 1) Operation name after 'mutation' or 'query'
                match = re.search(r"(mutation|query)\s+(\w+)", query, re.IGNORECASE)
                if match:
                    op_name = match.group(2).lower()
                    if op_name in PUBLIC_GRAPHQL_OPS:
                        return True
                # 2) First field name in the selection set
                field_match = re.search(r"\{\s*(\w+)", query)
                if field_match:
                    field_name = field_match.group(1).lower()
                    if field_name in PUBLIC_GRAPHQL_OPS:
                        return True
                # 3) Explicit operationName in request JSON
                op_name_json = parsed.get("operationName")
                if isinstance(op_name_json, str) and op_name_json.lower() in PUBLIC_GRAPHQL_OPS:
                    return True
            except Exception as e:
                log_msg("warn", f"Failed to parse GraphQL operation: {e}")
                return False

        return False
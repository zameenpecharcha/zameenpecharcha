import typing
from datetime import datetime
import strawberry
from gateway.app.exception.UserException import REException
from gateway.app.utils.log_utils import log_msg
from gateway.app.utils.grpc_client import AuthServiceClient
from typing import Optional

client = AuthServiceClient()

@strawberry.type
class AuthResponse:
    token: str
    refresh_token: Optional[str] = None

@strawberry.type
class OTPResponse:
    success: bool
    message: Optional[str] = None

@strawberry.type
class Query:
    @strawberry.field
    def verify_token(self, token: str) -> bool:
        try:
            response = client.verify_token(token)
            return response.is_valid
        except Exception as e:
            log_msg("error", f"Error verifying token: {str(e)}")
            raise REException("TOKEN_VERIFICATION_FAILED", "Failed to verify token", str(e)).to_graphql_error()

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def login(self, email: str, password: str) -> AuthResponse:
        try:
            response = client.login(email, password)
            return AuthResponse(
                token=response.token,
                refresh_token=response.refresh_token
            )
        except Exception as e:
            log_msg("error", f"Login failed for email {email}: {str(e)}")
            raise REException("LOGIN_FAILED", "Invalid credentials", str(e)).to_graphql_error()

    @strawberry.mutation
    async def send_otp(self, phone_number: str) -> OTPResponse:
        try:
            response = client.send_otp(phone_number)
            return OTPResponse(
                success=response.success,
                message="OTP sent successfully"
            )
        except Exception as e:
            log_msg("error", f"Failed to send OTP to {phone_number}: {str(e)}")
            raise REException("OTP_SEND_FAILED", "Failed to send OTP", str(e)).to_graphql_error()

    @strawberry.mutation
    async def verify_otp(self, phone_number: str, otp_code: str) -> AuthResponse:
        try:
            response = client.verify_otp(phone_number, otp_code)
            return AuthResponse(
                token=response.token
            )
        except Exception as e:
            log_msg("error", f"OTP verification failed for {phone_number}: {str(e)}")
            raise REException("OTP_VERIFICATION_FAILED", "Invalid OTP", str(e)).to_graphql_error()

    @strawberry.mutation
    async def forgot_password(self, email_or_phone: str) -> OTPResponse:
        try:
            response = client.forgot_password(email_or_phone)
            return OTPResponse(
                success=response.success,
                message="Password reset instructions sent"
            )
        except Exception as e:
            log_msg("error", f"Forgot password failed for {email_or_phone}: {str(e)}")
            raise REException("PASSWORD_RESET_FAILED", "Failed to process request", str(e)).to_graphql_error() 
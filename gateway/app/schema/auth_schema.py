import typing
import strawberry
from app.utils.grpc_client import auth_client
from app.utils.log_utils import log_msg
import grpc

@strawberry.type
class AuthResponse:
    success: bool
    token: typing.Optional[str] = None
    refresh_token: typing.Optional[str] = None
    message: typing.Optional[str] = None

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from Auth Service!"

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def login(self, email: str, password: str) -> AuthResponse:
        try:
            log_msg("info", f"Login attempt for {email}")
            response = auth_client.login(email, password)
            return AuthResponse(
                success=True,
                token=response.token,
                refresh_token=response.refresh_token,
                message="Login successful"
            )
        except grpc.RpcError as e:
            log_msg("error", f"Login error for {email}: {str(e)}")
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                return AuthResponse(success=False, message="Invalid credentials")
            return AuthResponse(success=False, message="Internal server error")

    @strawberry.mutation
    async def send_otp(self, email: str) -> AuthResponse:
        try:
            log_msg("info", f"Sending OTP to {email}")
            response = auth_client.send_otp(email)
            return AuthResponse(
                success=response.success,
                message="OTP sent successfully" if response.success else "Failed to send OTP"
            )
        except grpc.RpcError as e:
            log_msg("error", f"SendOTP error for {email}: {str(e)}")
            return AuthResponse(success=False, message="Failed to send OTP")

    @strawberry.mutation
    async def verify_otp(self, email: str, otp_code: str) -> AuthResponse:
        try:
            log_msg("info", f"Verifying OTP for {email}")
            response = auth_client.verify_otp(email, otp_code)
            if response.token:
                return AuthResponse(
                    success=True,
                    token=response.token,
                    message="OTP verified successfully"
                )
            return AuthResponse(success=False, message="Invalid OTP")
        except grpc.RpcError as e:
            log_msg("error", f"VerifyOTP error for {email}: {str(e)}")
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                return AuthResponse(success=False, message="Invalid OTP")
            return AuthResponse(success=False, message="Failed to verify OTP")

    @strawberry.mutation
    async def forgot_password(self, email: str) -> AuthResponse:
        try:
            log_msg("info", f"Forgot password request for {email}")
            response = auth_client.forgot_password(email)
            return AuthResponse(
                success=response.success,
                message="OTP sent successfully" if response.success else "Failed to send OTP"
            )
        except Exception as e:
            log_msg("error", f"ForgotPassword error for {email}: {str(e)}")
            return AuthResponse(success=False, message=str(e))

    @strawberry.mutation
    async def reset_password(
        self, email: str, otp_code: str, new_password: str
    ) -> AuthResponse:
        try:
            log_msg("info", f"Reset password request for {email}")
            response = auth_client.reset_password(
                email,
                otp_code,
                new_password
            )
            return AuthResponse(
                success=response.success,
                message="Password reset successfully" if response.success else "Failed to reset password"
            )
        except Exception as e:
            log_msg("error", f"ResetPassword error for {email}: {str(e)}")
            return AuthResponse(success=False, message=str(e)) 
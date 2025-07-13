from fastapi import APIRouter, HTTPException
from ..utils.grpc_client import AuthServiceClient
from pydantic import BaseModel

router = APIRouter()
auth_client = AuthServiceClient()

class LoginRequest(BaseModel):
    email: str
    password: str

class OTPRequest(BaseModel):
    phone_number: str

class VerifyOTPRequest(BaseModel):
    phone_number: str
    otp_code: str

class ForgotPasswordRequest(BaseModel):
    email_or_phone: str

class ResetPasswordRequest(BaseModel):
    email_or_phone: str
    otp_code: str
    new_password: str

@router.post("/login")
async def login(request: LoginRequest):
    try:
        response = auth_client.login(request.email, request.password)
        return {
            "token": response.token,
            "refresh_token": response.refresh_token
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/send-otp")
async def send_otp(request: OTPRequest):
    try:
        response = auth_client.send_otp(request.phone_number)
        return {"success": response.success}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send OTP")

@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    try:
        response = auth_client.verify_otp(request.phone_number, request.otp_code)
        return {"token": response.token}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid OTP")

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    try:
        response = auth_client.forgot_password(request.email_or_phone)
        return {"success": response.success}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to process forgot password request")

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    try:
        response = auth_client.reset_password(
            request.email_or_phone,
            request.otp_code,
            request.new_password
        )
        return {"success": response.success}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to reset password") 
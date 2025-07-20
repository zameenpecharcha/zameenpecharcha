import grpc
import bcrypt
import jwt
import random
import os
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from entity.user_entity import SessionLocal, User
import proto_files.auth_pb2 as auth_pb2
import proto_files.auth_pb2_grpc as auth_pb2_grpc
from utils.otp_utils import send_otp_email, send_otp_sms
from utils.redis_utils import store_otp, get_otp, delete_otp
from utils.log_utils import log_msg

# Load secret key from environment variables (ensure it's persistent)
SECRET_KEY = os.getenv("SECRET_KEY")

class AuthService(auth_pb2_grpc.AuthServiceServicer):

    def Login(self, request, context):
        correlation_id = context.peer()
        db: Session = SessionLocal()
        try:
            user = db.query(User).filter(User.email == request.email).first()
            if not user or not bcrypt.checkpw(request.password.encode(), user.password.encode()):
                log_msg("warning", "Invalid login attempt", user_id=request.email, correlation_id=correlation_id)
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid credentials")
                return auth_pb2.LoginResponse()

            token = jwt.encode({"email":  request.email, "exp": datetime.utcnow() + timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")
            refresh_token = jwt.encode({"email": request.email, "exp": datetime.utcnow() + timedelta(days=7)}, SECRET_KEY, algorithm="HS256")

            log_msg("info", "User logged in successfully", user_id=request.email, correlation_id=correlation_id)
            return auth_pb2.LoginResponse(token=token, refresh_token=refresh_token)
        except Exception as e:
            log_msg("error", f"Login error: {str(e)}", user_id=request.email, correlation_id=correlation_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Internal server error")
            return auth_pb2.LoginResponse()
        finally:
            db.close()

    def SendOTP(self, request, context):
        correlation_id = context.peer()
        try:
            otp_code = str(random.randint(100000, 999999))
            store_otp(request.phone_number, otp_code)
            if "@" in request.phone_number:
                send_otp_email(request.phone_number, otp_code)
            else:
                send_otp_sms(request.phone_number, otp_code)

            log_msg("info", f"OTP sent successfully", user_id=request.phone_number, correlation_id=correlation_id)
            return auth_pb2.OTPResponse(success=True)
        except Exception as e:
            log_msg("error", f"SendOTP error: {str(e)}", user_id=request.phone_number, correlation_id=correlation_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to send OTP")
            return auth_pb2.OTPResponse(success=False)

    def VerifyOTP(self, request, context):
        correlation_id = context.peer()
        try:
            stored_otp = get_otp(request.phone_number)
            if not stored_otp or stored_otp != request.otp_code:
                log_msg("warning", "Invalid OTP attempt", user_id=request.phone_number, correlation_id=correlation_id)
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid OTP")
                return auth_pb2.VerifyOTPResponse()

            token = jwt.encode({"email": request.phone_number, "exp": datetime.utcnow() + timedelta(hours=1)}, SECRET_KEY,
                               algorithm="HS256")
            delete_otp(request.phone_number)

            log_msg("info", "OTP verified successfully", user_id=request.phone_number, correlation_id=correlation_id)
            return auth_pb2.VerifyOTPResponse(token=token)
        except Exception as e:
            log_msg("error", f"VerifyOTP error: {str(e)}", user_id=request.phone_number, correlation_id=correlation_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to verify OTP")
            return auth_pb2.VerifyOTPResponse()

    def ForgotPassword(self, request, context):
        correlation_id = context.peer()
        try:
            otp_code = str(random.randint(100000, 999999))
            store_otp(request.email_or_phone, otp_code)

            if "@" in request.email_or_phone:
                send_otp_email(request.email_or_phone, otp_code)
            else:
                send_otp_sms(request.email_or_phone, otp_code)

            log_msg("info", "Forgot password OTP sent", user_id=request.email_or_phone, correlation_id=correlation_id)
            return auth_pb2.ForgotPasswordResponse(success=True)
        except Exception as e:
            log_msg("error", f"ForgotPassword error: {str(e)}", user_id=request.email_or_phone, correlation_id=correlation_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to send OTP for password reset")
            return auth_pb2.ForgotPasswordResponse(success=False)

    def ResetPassword(self, request, context):
        correlation_id = context.peer()
        db: Session = SessionLocal()
        try:
            stored_otp = get_otp(request.email_or_phone)
            if not stored_otp or stored_otp != request.otp_code:
                log_msg("warning", "Invalid OTP for password reset", user_id=request.email_or_phone, correlation_id=correlation_id)
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid OTP")
                return auth_pb2.ResetPasswordResponse(success=False)

            user = db.query(User).filter(User.email == request.email_or_phone).first()
            if user:
                hashed_password = bcrypt.hashpw(request.new_password.encode(), bcrypt.gensalt()).decode('utf-8')
                user.password = hashed_password
                db.commit()
                log_msg("info", "Password reset successfully", user_id=request.email_or_phone, correlation_id=correlation_id)
                return auth_pb2.ResetPasswordResponse(success=True)

            log_msg("error", "User not found", user_id=request.email_or_phone, correlation_id=correlation_id)
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            return auth_pb2.ResetPasswordResponse(success=False)
        except Exception as e:
            db.rollback()
            log_msg("error", f"ResetPassword error: {str(e)}", user_id=request.email_or_phone, correlation_id=correlation_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to reset password")
            return auth_pb2.ResetPasswordResponse(success=False)
        finally:
            db.close()

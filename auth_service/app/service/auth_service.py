import grpc
import bcrypt
import jwt
import random
import os
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.entity.user_entity import SessionLocal, User
import app.proto_files.auth_pb2 as auth_pb2
import app.proto_files.auth_pb2_grpc as auth_pb2_grpc
from app.utils.otp_utils import send_otp_email, send_otp_sms
from app.utils.redis_utils import store_otp, get_otp, delete_otp
from app.utils.log_utils import log_msg

# Load secret key from environment variables (ensure it's persistent)
SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_key_here")

class AuthService(auth_pb2_grpc.AuthServiceServicer):

    def Login(self, request, context):
        correlation_id = context.peer()
        db: Session = SessionLocal()
        try:
            print(f"Login attempt for email: {request.email}")
            user = db.query(User).filter(User.email == request.email).first()
            
            if not user:
                print(f"User not found: {request.email}")
                log_msg("warning", "User not found", user_id=request.email, correlation_id=correlation_id)
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid credentials")
                return auth_pb2.LoginResponse()
                
            try:
                password_matches = bcrypt.checkpw(request.password.encode(), user.password.encode())
            except Exception as e:
                print(f"Password verification error: {str(e)}")
                password_matches = False
                
            if not password_matches:
                print(f"Invalid password for user: {request.email}")
                log_msg("warning", "Invalid password", user_id=request.email, correlation_id=correlation_id)
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid credentials")
                return auth_pb2.LoginResponse()

            token = jwt.encode({"email": request.email, "exp": datetime.utcnow() + timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")
            refresh_token = jwt.encode({"email": request.email, "exp": datetime.utcnow() + timedelta(days=7)}, SECRET_KEY, algorithm="HS256")

            print(f"Login successful for user: {request.email}")
            log_msg("info", "User logged in successfully", user_id=request.email, correlation_id=correlation_id)
            return auth_pb2.LoginResponse(token=token, refresh_token=refresh_token)
        except Exception as e:
            print(f"Login error: {str(e)}")
            log_msg("error", f"Login error: {str(e)}", user_id=request.email, correlation_id=correlation_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return auth_pb2.LoginResponse()
        finally:
            db.close()

    def SendOTP(self, request, context):
        correlation_id = context.peer()
        try:
            otp_code = str(random.randint(100000, 999999))
            print(f"Generated OTP {otp_code} for {request.email}")
            
            # Store OTP
            if store_otp(request.email, otp_code):
                print(f"OTP stored successfully for {request.email}")
            else:
                print(f"Failed to store OTP for {request.email}")
                
            # Send OTP via email
            send_otp_email(request.email, otp_code)

            log_msg("info", f"OTP sent successfully", user_id=request.email, correlation_id=correlation_id)
            return auth_pb2.OTPResponse(success=True)
        except Exception as e:
            print(f"SendOTP error: {str(e)}")
            log_msg("error", f"SendOTP error: {str(e)}", user_id=request.email, correlation_id=correlation_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to send OTP")
            return auth_pb2.OTPResponse(success=False)

    def VerifyOTP(self, request, context):
        correlation_id = context.peer()
        try:
            print(f"Verifying OTP for {request.email}")
            stored_otp = get_otp(request.email)
            print(f"Stored OTP: {stored_otp}, Received OTP: {request.otp_code}")
            
            if not stored_otp:
                print(f"No OTP found for {request.email}")
                log_msg("warning", "No OTP found", user_id=request.email, correlation_id=correlation_id)
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid OTP")
                return auth_pb2.VerifyOTPResponse()
                
            if stored_otp != request.otp_code:
                print(f"OTP mismatch for {request.email}")
                log_msg("warning", "OTP mismatch", user_id=request.email, correlation_id=correlation_id)
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid OTP")
                return auth_pb2.VerifyOTPResponse()

            token = jwt.encode({"email": request.email, "exp": datetime.utcnow() + timedelta(hours=1)}, SECRET_KEY,
                               algorithm="HS256")
            delete_otp(request.email)
            print(f"OTP verified successfully for {request.email}")

            log_msg("info", "OTP verified successfully", user_id=request.email, correlation_id=correlation_id)
            return auth_pb2.VerifyOTPResponse(token=token)
        except Exception as e:
            print(f"VerifyOTP error: {str(e)}")
            log_msg("error", f"VerifyOTP error: {str(e)}", user_id=request.email, correlation_id=correlation_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to verify OTP")
            return auth_pb2.VerifyOTPResponse()

    def ForgotPassword(self, request, context):
        correlation_id = context.peer()
        try:
            otp_code = str(random.randint(100000, 999999))
            print(f"Generated OTP {otp_code} for forgot password request: {request.email_or_phone}")
            
            # Store OTP
            if store_otp(request.email_or_phone, otp_code):
                print(f"OTP stored successfully for {request.email_or_phone}")
            else:
                print(f"Failed to store OTP for {request.email_or_phone}")

            if "@" in request.email_or_phone:
                send_otp_email(request.email_or_phone, otp_code)
            else:
                send_otp_sms(request.email_or_phone, otp_code)

            log_msg("info", "Forgot password OTP sent", user_id=request.email_or_phone, correlation_id=correlation_id)
            return auth_pb2.ForgotPasswordResponse(success=True)
        except Exception as e:
            print(f"ForgotPassword error: {str(e)}")
            log_msg("error", f"ForgotPassword error: {str(e)}", user_id=request.email_or_phone, correlation_id=correlation_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to send OTP for password reset")
            return auth_pb2.ForgotPasswordResponse(success=False)

    def ResetPassword(self, request, context):
        correlation_id = context.peer()
        db: Session = SessionLocal()
        try:
            print(f"Resetting password for {request.email_or_phone}")
            stored_otp = get_otp(request.email_or_phone)
            print(f"Stored OTP: {stored_otp}, Received OTP: {request.otp_code}")
            
            if not stored_otp:
                print(f"No OTP found for {request.email_or_phone}")
                log_msg("warning", "No OTP found", user_id=request.email_or_phone, correlation_id=correlation_id)
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid OTP")
                return auth_pb2.ResetPasswordResponse(success=False)
                
            if stored_otp != request.otp_code:
                print(f"OTP mismatch for {request.email_or_phone}")
                log_msg("warning", "OTP mismatch", user_id=request.email_or_phone, correlation_id=correlation_id)
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid OTP")
                return auth_pb2.ResetPasswordResponse(success=False)

            user = db.query(User).filter(User.email == request.email_or_phone).first()
            if user:
                hashed_password = bcrypt.hashpw(request.new_password.encode(), bcrypt.gensalt()).decode('utf-8')
                user.password = hashed_password
                db.commit()
                delete_otp(request.email_or_phone)
                print(f"Password reset successful for {request.email_or_phone}")
                log_msg("info", "Password reset successfully", user_id=request.email_or_phone, correlation_id=correlation_id)
                return auth_pb2.ResetPasswordResponse(success=True)

            print(f"User not found: {request.email_or_phone}")
            log_msg("error", "User not found", user_id=request.email_or_phone, correlation_id=correlation_id)
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            return auth_pb2.ResetPasswordResponse(success=False)
        except Exception as e:
            print(f"ResetPassword error: {str(e)}")
            db.rollback()
            log_msg("error", f"ResetPassword error: {str(e)}", user_id=request.email_or_phone, correlation_id=correlation_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to reset password")
            return auth_pb2.ResetPasswordResponse(success=False)
        finally:
            db.close()

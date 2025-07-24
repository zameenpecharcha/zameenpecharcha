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
            # Generate and store OTP
            otp_code = str(random.randint(100000, 999999))
            print(f"\n=== SendOTP ===")
            print(f"Generated new OTP {otp_code} for {request.email}")
            
            # Store OTP
            store_success = store_otp(request.email, otp_code)
            if not store_success:
                print(f"Failed to store OTP for {request.email}")
                raise Exception("Failed to store OTP")

            # For testing purposes, print the OTP
            print(f"TEST MODE: OTP for {request.email} is {otp_code}")
            
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
            print(f"\n=== VerifyOTP START ===")
            print(f"Verifying OTP for {request.email}")
            print(f"Received OTP code: {request.otp_code}")
            
            stored_otp = get_otp(request.email)
            print(f"Retrieved stored OTP: {stored_otp}")
            print(f"OTPs match: {stored_otp == request.otp_code}")
            
            if not stored_otp:
                print(f"No OTP found for {request.email}")
                log_msg("warning", "No OTP found", user_id=request.email, correlation_id=correlation_id)
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid OTP")
                return auth_pb2.VerifyOTPResponse()
                
            if stored_otp != request.otp_code:
                print(f"OTP mismatch for {request.email}")
                print(f"Stored OTP: {stored_otp}")
                print(f"Received OTP: {request.otp_code}")
                log_msg("warning", "OTP mismatch", user_id=request.email, correlation_id=correlation_id)
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid OTP")
                return auth_pb2.VerifyOTPResponse()

            print(f"OTP verified successfully for {request.email}")

            # Generate token
            token = jwt.encode(
                {"email": request.email, "exp": datetime.utcnow() + timedelta(hours=1)},
                SECRET_KEY,
                algorithm="HS256"
            )

            log_msg("info", "OTP verified successfully", user_id=request.email, correlation_id=correlation_id)
            return auth_pb2.VerifyOTPResponse(token=token)
        except Exception as e:
            print(f"VerifyOTP error: {str(e)}")
            log_msg("error", f"VerifyOTP error: {str(e)}", user_id=request.email, correlation_id=correlation_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to verify OTP")
            return auth_pb2.VerifyOTPResponse()
        finally:
            print("=== VerifyOTP END ===\n")

    def ForgotPassword(self, request, context):
        correlation_id = context.peer()
        print(f"\n=== ForgotPassword START ===")
        print(f"Request received for: {request.email}")
        
        try:
            # Generate OTP
            otp = ''.join(random.choices('0123456789', k=6))
            print(f"Generated OTP: {otp}")
            
            # Store OTP
            print(f"Attempting to store OTP for {request.email}")
            store_success = store_otp(request.email, otp)
            print(f"OTP store result: {store_success}")
            
            if not store_success:
                print("Failed to store OTP")
                log_msg("error", "Failed to store OTP", user_id=request.email, correlation_id=correlation_id)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to store OTP")
                return auth_pb2.ForgotPasswordResponse(success=False)
            
            # Verify OTP was stored
            print(f"Verifying OTP storage...")
            stored_otp = get_otp(request.email)
            print(f"Verification - Retrieved OTP: {stored_otp}")
            print(f"Verification - Expected OTP: {otp}")
            print(f"Verification - OTPs match: {stored_otp == otp}")
            
            if stored_otp != otp:
                print("OTP verification failed - stored OTP doesn't match generated OTP")
                log_msg("error", "OTP storage verification failed", user_id=request.email, correlation_id=correlation_id)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to store OTP")
                return auth_pb2.ForgotPasswordResponse(success=False)
            
            # Send OTP via email
            try:
                # TODO: Implement actual email sending
                print(f"Would send email to {request.email} with OTP: {otp}")
                print("FOR TESTING - USE THIS OTP: " + otp)
                log_msg("info", "OTP email would be sent (not implemented)", user_id=request.email, correlation_id=correlation_id)
            except Exception as e:
                print(f"Failed to send email: {str(e)}")
                # Don't fail the request if email fails, just log it
                log_msg("warning", f"Failed to send OTP email: {str(e)}", user_id=request.email, correlation_id=correlation_id)
            
            print("ForgotPassword completed successfully")
            log_msg("info", "ForgotPassword successful", user_id=request.email, correlation_id=correlation_id)
            return auth_pb2.ForgotPasswordResponse(success=True)
            
        except Exception as e:
            print(f"Error in ForgotPassword: {str(e)}")
            log_msg("error", f"ForgotPassword error: {str(e)}", user_id=request.email, correlation_id=correlation_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_pb2.ForgotPasswordResponse(success=False)
        finally:
            print("=== ForgotPassword END ===\n")

    def ResetPassword(self, request, context):
        correlation_id = context.peer()
        db: Session = SessionLocal()
        try:
            print(f"\n=== ResetPassword START ===")
            print(f"Resetting password for {request.email}")
            print(f"Received OTP code: {request.otp_code}")
            
            stored_otp = get_otp(request.email)
            print(f"Retrieved stored OTP: {stored_otp}")
            print(f"OTPs match: {stored_otp == request.otp_code}")
            
            if not stored_otp:
                print(f"No OTP found for {request.email}")
                log_msg("warning", "No OTP found", user_id=request.email, correlation_id=correlation_id)
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid OTP")
                return auth_pb2.ResetPasswordResponse(success=False)
                
            if stored_otp != request.otp_code:
                print(f"OTP mismatch for {request.email}")
                print(f"Stored OTP: {stored_otp}")
                print(f"Received OTP: {request.otp_code}")
                log_msg("warning", "OTP mismatch", user_id=request.email, correlation_id=correlation_id)
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid OTP")
                return auth_pb2.ResetPasswordResponse(success=False)

            user = db.query(User).filter(User.email == request.email).first()
            if user:
                # Delete OTP after successful verification
                print("OTP verified successfully, deleting it...")
                delete_otp(request.email)
                
                # Update password
                print("Updating password...")
                hashed_password = bcrypt.hashpw(request.new_password.encode(), bcrypt.gensalt()).decode('utf-8')
                user.password = hashed_password
                db.commit()
                print(f"Password reset successful for {request.email}")
                log_msg("info", "Password reset successfully", user_id=request.email, correlation_id=correlation_id)
                return auth_pb2.ResetPasswordResponse(success=True)

            print(f"User not found: {request.email}")
            log_msg("error", "User not found", user_id=request.email, correlation_id=correlation_id)
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            return auth_pb2.ResetPasswordResponse(success=False)
        except Exception as e:
            print(f"ResetPassword error: {str(e)}")
            db.rollback()
            log_msg("error", f"ResetPassword error: {str(e)}", user_id=request.email, correlation_id=correlation_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to reset password")
            return auth_pb2.ResetPasswordResponse(success=False)
        finally:
            db.close()
            print("=== ResetPassword END ===\n")

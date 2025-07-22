import os
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText

def send_otp_sms(phone_number, otp_code):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
    if not all([account_sid, auth_token, twilio_number]):
        print("Twilio credentials are not set in environment variables.")
        return
    client = Client(account_sid, auth_token)
    message = f"Your OTP code is: {otp_code}"
    try:
        client.messages.create(
            body=message,
            from_=twilio_number,
            to=phone_number
        )
        print(f"OTP sent via SMS to {phone_number}")
    except Exception as e:
        print(f"Failed to send OTP SMS: {e}")

def send_otp_email(email, otp_code):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("FROM_EMAIL")
    if not all([smtp_server, smtp_port, smtp_user, smtp_password, from_email]):
        print("SMTP credentials are not set in environment variables.")
        return
    subject = "Your OTP Code"
    body = f"Your OTP code is: {otp_code}"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, [email], msg.as_string())
        print(f"OTP sent via Email to {email}")
    except Exception as e:
        print(f"Failed to send OTP Email: {e}") 
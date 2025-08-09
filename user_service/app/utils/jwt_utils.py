import jwt
import os

# For testing, use a simple secret key
SECRET_KEY = "your-256-bit-secret"

def verify_jwt_token(token):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]  # Use HS256 for testing
        )
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.ImmatureSignatureError:
        return None, "Token not valid yet (nbf)"
    except jwt.InvalidTokenError as e:
        return None, f"Invalid token: {str(e)}"
    except Exception as e:
        return None, f"Token verification error: {str(e)}"
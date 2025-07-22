import os
import redis

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.StrictRedis(
    host=redis_host,
    port=redis_port,
    decode_responses=True,
    socket_connect_timeout=5,  # seconds
    socket_timeout=5           # seconds
)

def store_otp(phone_or_email, otp):
    try:
        redis_client.setex(phone_or_email, 300, otp)  # OTP expires in 5 mins
    except Exception as e:
        print(f"Redis error in store_otp: {e}", flush=True)

def get_otp(phone_or_email):
    return redis_client.get(phone_or_email)

def delete_otp(phone_or_email):
    redis_client.delete(phone_or_email)

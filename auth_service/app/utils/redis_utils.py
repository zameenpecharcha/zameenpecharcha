import redis

# Connect to Redis
redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)

def store_otp(phone_or_email, otp):
    redis_client.setex(phone_or_email, 300, otp)  # OTP expires in 5 mins

def get_otp(phone_or_email):
    return redis_client.get(phone_or_email)

def delete_otp(phone_or_email):
    redis_client.delete(phone_or_email)

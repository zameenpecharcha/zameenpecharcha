import os
import redis
from dotenv import load_dotenv

# Initialize in-memory store as fallback
memory_store = {}

def get_redis_client():
    try:
        load_dotenv()
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        
        print(f"Attempting to connect to Redis at {redis_host}:{redis_port}")
        
        client = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            socket_connect_timeout=2,  # Reduced timeout
            socket_timeout=2           # Reduced timeout
        )
        
        # Test the connection
        client.ping()
        print("Connected to Redis successfully!")
        return client
    except Exception as e:
        print(f"Redis connection error: {str(e)}")
        return None

# Initialize Redis client
redis_client = get_redis_client()

def store_otp(phone_or_email, otp):
    if not redis_client:
        print(f"Redis not available, storing OTP {otp} in memory for {phone_or_email}")
        # Store in memory as fallback
        memory_store[phone_or_email] = otp
        print(f"Current memory store: {memory_store}")
        return True
    try:
        redis_client.setex(phone_or_email, 300, otp)  # OTP expires in 5 mins
        print(f"OTP {otp} stored in Redis for {phone_or_email}")
        return True
    except Exception as e:
        print(f"Redis error in store_otp: {e}", flush=True)
        # Fallback to memory storage on Redis error
        memory_store[phone_or_email] = otp
        print(f"Fallback: OTP stored in memory. Current store: {memory_store}")
        return True

def get_otp(phone_or_email):
    if not redis_client:
        print(f"Redis not available, getting OTP from memory for {phone_or_email}")
        otp = memory_store.get(phone_or_email)
        print(f"OTP from memory: {otp}")
        print(f"Current memory store: {memory_store}")
        return otp
    try:
        otp = redis_client.get(phone_or_email)
        print(f"OTP from Redis for {phone_or_email}: {otp}")
        return otp
    except Exception as e:
        print(f"Redis error in get_otp: {e}", flush=True)
        # Fallback to memory storage on Redis error
        otp = memory_store.get(phone_or_email)
        print(f"Fallback: OTP from memory: {otp}")
        print(f"Current memory store: {memory_store}")
        return otp

def delete_otp(phone_or_email):
    if not redis_client:
        print(f"Redis not available, deleting OTP from memory for {phone_or_email}")
        # Delete from memory as fallback
        if phone_or_email in memory_store:
            del memory_store[phone_or_email]
            print(f"OTP deleted from memory for {phone_or_email}")
        print(f"Current memory store: {memory_store}")
        return
    try:
        redis_client.delete(phone_or_email)
        print(f"OTP deleted from Redis for {phone_or_email}")
    except Exception as e:
        print(f"Redis error in delete_otp: {e}", flush=True)
        # Fallback to memory storage on Redis error
        if phone_or_email in memory_store:
            del memory_store[phone_or_email]
            print(f"Fallback: OTP deleted from memory for {phone_or_email}")
        print(f"Current memory store: {memory_store}")

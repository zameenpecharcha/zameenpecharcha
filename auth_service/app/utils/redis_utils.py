import os
import redis
from dotenv import load_dotenv

# Create a singleton instance of OTPStore at module level
class OTPStore:
    _instance = None
    _store = {}  # Move store to class variable
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OTPStore, cls).__new__(cls)
            print("Created new OTPStore instance")
        return cls._instance

    def __init__(self):
        print("OTPStore instance accessed")
            
    def set(self, key, value):
        print(f"\n=== OTPStore.set ===")
        print(f"Storing OTP. Key: {key}, Value: {value}")
        OTPStore._store[key] = value  # Use class variable
        print(f"Store contents after set: {OTPStore._store}")
        # Verify storage
        stored_value = OTPStore._store.get(key)
        print(f"Verification - Retrieved value: {stored_value}")
        print(f"=== OTPStore.set END ===\n")
        return stored_value == value

    def get(self, key):
        print(f"\n=== OTPStore.get ===")
        print(f"Retrieving OTP for key: {key}")
        value = OTPStore._store.get(key)
        print(f"Retrieved value: {value}")
        print(f"Current store contents: {OTPStore._store}")
        print(f"=== OTPStore.get END ===\n")
        return value

    def delete(self, key):
        print(f"\n=== OTPStore.delete ===")
        print(f"Deleting OTP for key: {key}")
        print(f"Store contents before delete: {OTPStore._store}")
        if key in OTPStore._store:
            del OTPStore._store[key]
            print(f"OTP deleted for key: {key}")
        else:
            print(f"Key not found in store: {key}")
        print(f"Store contents after delete: {OTPStore._store}")
        print(f"=== OTPStore.delete END ===\n")

# Create the singleton instance
otp_store = OTPStore()
print("OTP Store singleton created")

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
            socket_connect_timeout=2,
            socket_timeout=2
        )
        
        client.ping()
        print("Connected to Redis successfully!")
        return client
    except Exception as e:
        print(f"Redis connection error: {str(e)}")
        return None

# Initialize Redis client
redis_client = get_redis_client()

def store_otp(phone_or_email, otp):
    print(f"\n=== store_otp ===")
    print(f"Storing OTP {otp} for {phone_or_email}")
    
    if not redis_client:
        print("Redis not available, using memory store")
        success = otp_store.set(phone_or_email, otp)
        if success:
            print("OTP stored successfully in memory")
        else:
            print("Failed to store OTP in memory")
        return success
        
    try:
        redis_client.setex(phone_or_email, 300, otp)  # OTP expires in 5 mins
        print(f"OTP stored successfully in Redis")
        return True
    except Exception as e:
        print(f"Redis error: {e}")
        print("Falling back to memory store")
        return otp_store.set(phone_or_email, otp)
    finally:
        print("=== store_otp END ===\n")

def get_otp(phone_or_email):
    print(f"\n=== get_otp ===")
    print(f"Retrieving OTP for {phone_or_email}")
    
    if not redis_client:
        print("Redis not available, using memory store")
        otp = otp_store.get(phone_or_email)
        print(f"Retrieved OTP from memory: {otp}")
        return otp
        
    try:
        otp = redis_client.get(phone_or_email)
        print(f"Retrieved OTP from Redis: {otp}")
        return otp
    except Exception as e:
        print(f"Redis error: {e}")
        print("Falling back to memory store")
        otp = otp_store.get(phone_or_email)
        print(f"Retrieved OTP from memory: {otp}")
        return otp
    finally:
        print("=== get_otp END ===\n")

def delete_otp(phone_or_email):
    print(f"\n=== delete_otp ===")
    print(f"Deleting OTP for {phone_or_email}")
    
    if not redis_client:
        print("Redis not available, using memory store")
        otp_store.delete(phone_or_email)
        return
        
    try:
        redis_client.delete(phone_or_email)
        print("OTP deleted from Redis")
    except Exception as e:
        print(f"Redis error: {e}")
        print("Falling back to memory store")
        otp_store.delete(phone_or_email)
    finally:
        print("=== delete_otp END ===\n")

print("\nRedis utils initialized with memory store fallback")

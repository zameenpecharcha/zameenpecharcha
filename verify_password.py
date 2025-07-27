import bcrypt

password = "newpassword1234"
hashed = "$2b$12$V8g.NAC4fSmglywF/xT8iOGHLv396HCxNy9H19OEB2ZTQauqJfRf."

try:
    matches = bcrypt.checkpw(password.encode(), hashed.encode())
    print(f"Password matches: {matches}")
except Exception as e:
    print(f"Error: {str(e)}")

# Also try generating a new hash for comparison
new_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
print(f"\nNew hash for same password: {new_hash}") 
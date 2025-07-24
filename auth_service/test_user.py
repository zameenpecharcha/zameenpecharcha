from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import bcrypt
from app.entity.user_entity import User, Base
from sqlalchemy.orm import sessionmaker

def test_user():
    load_dotenv()
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT", "5434"))
    DB_NAME = os.getenv("DB_NAME", "postgres")
    
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(DATABASE_URL)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Try to find the user
        user = session.query(User).filter(User.email == "Hello").first()
        if user:
            print("\nUser found:")
            print(f"Email: {user.email}")
            print(f"Raw stored password: {user.password}")
            print("\nTesting password verification:")
            
            test_password = "Hello"
            print(f"Test password: {test_password}")
            print(f"Test password encoded: {test_password.encode()}")
            
            try:
                # Try to verify password
                is_valid = bcrypt.checkpw(test_password.encode(), user.password.encode())
                print(f"Password verification result: {is_valid}")
            except Exception as e:
                print(f"Error during password verification: {str(e)}")
                
            # Create new test password hash for comparison
            new_hash = bcrypt.hashpw("Hello".encode(), bcrypt.gensalt()).decode()
            print(f"\nNew hash for same password: {new_hash}")
            
            # Update the password in database
            print("\nUpdating password in database...")
            user.password = new_hash
            session.commit()
            print("Password updated successfully!")
            
        else:
            print("\nUser not found. Creating test user...")
            # Create a test user with properly hashed password
            hashed_password = bcrypt.hashpw("Hello".encode(), bcrypt.gensalt()).decode()
            print(f"Created hash: {hashed_password}")
            
            new_user = User(
                email="Hello",
                password=hashed_password,
                name="Test User"
            )
            session.add(new_user)
            session.commit()
            print("Test user created successfully!")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    test_user() 
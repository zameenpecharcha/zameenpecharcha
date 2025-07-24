from sqlalchemy.orm import sessionmaker
from app.entity.user_entity import User, SessionLocal
from app.utils.db_connection import get_db_engine

def list_users():
    session = SessionLocal()
    try:
        users = session.query(User).all()
        print("\nExisting users in database:")
        print("-" * 50)
        for user in users:
            print(f"Email: {user.email}")
            print(f"Name: {user.name}")
            print("-" * 50)
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    list_users() 
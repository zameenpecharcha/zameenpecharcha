from user_service.app.entity.user_entity import users
from sqlalchemy.orm import sessionmaker
from user_service.app.utils.db_connection import get_db_engine
from sqlalchemy import select
import uuid

SessionLocal = sessionmaker(bind=get_db_engine())

class UserRow:
    def __init__(self, user_id, name, email, phone, password, role, location):
        self.user_id = str(user_id)  # Convert UUID to string
        self.name = str(name)
        self.email = str(email)
        self.phone = str(phone) if phone else None  # Changed to string
        self.password = str(password)
        self.role = str(role) if role else None
        self.location = str(location) if location else None

def get_user_by_id(id_str):
    session = SessionLocal()
    try:
        # Convert string to UUID
        try:
            user_id = uuid.UUID(id_str)
        except ValueError:
            return None

        query = select(
            users.c.user_id,
            users.c.name,
            users.c.email,
            users.c.phone,
            users.c.password,
            users.c.role,
            users.c.location
        ).where(users.c.user_id == user_id)
        result = session.execute(query).fetchone()
        if result:
            return UserRow(*result)
        return None
    finally:
        session.close()

def create_user(name, email, phone, password, role=None, location=None):
    session = SessionLocal()
    try:
        # Generate UUID for new user
        user_id = uuid.uuid4()
        result = session.execute(users.insert().returning(users.c.user_id).values(
            user_id=user_id,
            name=name,
            email=email,
            phone=phone,
            password=password,
            role=role,
            location=location
        ))
        session.commit()
        return str(result.scalar())  # Convert UUID to string before returning
    finally:
        session.close()

from user_service.app.entity.user_entity import users
from sqlalchemy.orm import sessionmaker
from user_service.app.utils.db_connection import get_db_engine
from sqlalchemy import select

SessionLocal = sessionmaker(bind=get_db_engine())

class UserRow:
    def __init__(self, user_id, name, email, phone, password, role, location):
        self.user_id = int(user_id)
        self.name = str(name)
        self.email = str(email)
        self.phone = int(phone) if phone else None
        self.password = str(password)
        self.role = str(role) if role else None
        self.location = str(location) if location else None

def get_user_by_id(id):
    session = SessionLocal()
    try:
        query = select(
            users.c.user_id,
            users.c.name,
            users.c.email,
            users.c.phone,
            users.c.password,
            users.c.role,
            users.c.location
        ).where(users.c.user_id == id)
        result = session.execute(query).fetchone()
        if result:
            return UserRow(*result)
        return None
    finally:
        session.close()

def create_user(name, email, phone, password, role=None, location=None):
    session = SessionLocal()
    try:
        result = session.execute(users.insert().returning(users.c.user_id).values(
            name=name,
            email=email,
            phone=phone,
            password=password,
            role=role,
            location=location
        ))
        session.commit()
        return result.scalar()  # This will return the inserted user_id
    finally:
        session.close()

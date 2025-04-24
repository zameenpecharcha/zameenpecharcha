from user_service.app.entity.user_entity import users
from sqlalchemy.orm import sessionmaker
from user_service.app.utils.db_connection import get_db_engine

SessionLocal = sessionmaker(bind=get_db_engine())

def get_user_by_id(user_id):
    session = SessionLocal()
    user = session.execute(users.select().where(users.c.user_id == user_id)).fetchone()
    session.close()
    return user

def create_user(name, email, phone, password):
    session = SessionLocal()
    result = session.execute(users.insert().returning(users.c.user_id).values(
        name=name, email=email, phone=phone, password=password
    ))
    session.commit()
    session.close()
    return result.scalar()  # This will return the inserted user_id


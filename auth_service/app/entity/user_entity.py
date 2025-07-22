from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, TIMESTAMP
from utils.db_connection import get_db_engine

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    email = Column(String(50), unique=True, nullable=False)
    phone = Column(Integer)
    profile_photo = Column(String(50))
    role = Column(String(50))
    location = Column(String(50))
    created_at = Column(TIMESTAMP)
    bio = Column(String(50))
    password = Column(String(100), nullable=False)

# Initialize the database session
SessionLocal = sessionmaker(bind=get_db_engine())


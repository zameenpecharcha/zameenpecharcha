from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, TIMESTAMP, create_engine, text
from app.utils.db_connection import get_db_engine
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    email = Column(String(50), unique=True, nullable=False)
    phone = Column(String(15))  # Changed to String to handle phone numbers better
    profile_photo = Column(String(255))  # Increased length for URLs
    role = Column(String(50))
    location = Column(String(100))  # Increased length for addresses
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    bio = Column(String(500))  # Increased length for bios
    password = Column(String(100), nullable=False)

# Initialize the database engine
engine = get_db_engine()

# Only create tables if they don't exist
Base.metadata.create_all(engine)

print("Database tables verified!")

# Initialize the database session
SessionLocal = sessionmaker(bind=engine)


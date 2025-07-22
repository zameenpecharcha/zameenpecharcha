from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db_engine():
    # Get database connection details from environment variables or use defaults
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "zameenpecharcha")

    # Create database URL
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Create engine
    engine = create_engine(DATABASE_URL)
    
    try:
        # Test the connection
        with engine.connect() as conn:
            print("Connected to PostgreSQL database successfully!")
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        raise

    return engine

# Create declarative base
Base = declarative_base() 
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
import os
from dotenv import load_dotenv
import logging
from pathlib import Path
from ..entity.comment_entity import Base

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    # Load environment variables
    load_dotenv()

    # Get database configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "postgres")  # Using postgres as default
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_PORT = os.getenv("DB_PORT", "5432")

    try:
        # Since we're using the postgres database, we don't need to create it
        # Just connect and create tables
        engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        # Create all tables
        Base.metadata.create_all(engine)
        logger.info("All tables created successfully")
        
        return True

    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_database() 
from sqlalchemy import create_engine, MetaData
from user_service.app.entity.user_entity import users
from user_service.app.utils.db_connection import get_db_engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    try:
        # Get database engine
        engine = get_db_engine()
        
        # Create MetaData instance
        metadata = MetaData()
        
        # Create all tables (in this case, just users table)
        users.metadata.create_all(engine)
        
        logger.info("Users table created successfully!")
        
    except Exception as e:
        logger.error(f"Error creating users table: {str(e)}")
        raise

if __name__ == "__main__":
    init_db() 
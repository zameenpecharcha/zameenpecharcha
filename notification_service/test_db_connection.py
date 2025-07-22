from app.utils.init_db import init_database
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    try:
        # Initialize database and create tables
        init_database()
        logger.info("Database connection test successful!")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection() 
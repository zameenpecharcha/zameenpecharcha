import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from dotenv import load_dotenv
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """Create the database if it doesn't exist."""
    load_dotenv()

    # Get database configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "notification_db")  # Changed to a specific database name
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_PORT = os.getenv("DB_PORT", "5432")

    # First connect to default postgres database to create our database
    postgres_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
    
    try:
        engine = create_engine(postgres_url)
        
        with engine.connect() as conn:
            # Disconnect all users from the database
            conn.execute(text(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{DB_NAME}'
                AND pid <> pg_backend_pid()
            """))
            conn.commit()
            
            # Drop database if exists
            conn.execute(text(f"DROP DATABASE IF EXISTS {DB_NAME}"))
            conn.commit()
            
            # Create database
            conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
            conn.commit()
            
            logger.info(f"Database '{DB_NAME}' created successfully")
            
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        raise

    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def create_tables(db_url):
    """Create all necessary tables."""
    try:
        # Import here to avoid circular imports
        from ..entity.notification import Base
        
        engine = create_engine(db_url)
        Base.metadata.create_all(engine)
        logger.info("All tables created successfully")
        
        return engine
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise

def insert_test_data(engine):
    """Insert some test data."""
    try:
        from ..entity.notification import Notification, LocationSubscription
        from sqlalchemy.orm import sessionmaker
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create test notifications
        notifications = [
            Notification(
                user_id=10,
                type="post_like",
                message="User 5 liked your post",
                entity_id=1,
                entity_type="post",
                is_read=False,
                created_at=datetime.utcnow(),
                context='{"liker_id": 5}'
            ),
            Notification(
                user_id=10,
                type="comment",
                message="User 6 commented on your post",
                entity_id=1,
                entity_type="post",
                is_read=False,
                created_at=datetime.utcnow(),
                context='{"commenter_id": 6, "comment_text": "Great post!"}'
            ),
            Notification(
                user_id=10,
                type="trending_post",
                message="Your post is trending in Hyderabad",
                entity_id=1,
                entity_type="post",
                is_read=True,
                created_at=datetime.utcnow(),
                context='{"location": "Hyderabad"}'
            )
        ]
        
        # Create test location subscriptions
        subscriptions = [
            LocationSubscription(
                user_id=10,
                latitude=17.385044,
                longitude=78.486671,
                radius_km=10.0,
                is_active=True,
                created_at=datetime.utcnow()
            ),
            LocationSubscription(
                user_id=10,
                latitude=17.441883,
                longitude=78.391588,
                radius_km=5.0,
                is_active=True,
                created_at=datetime.utcnow()
            )
        ]
        
        session.add_all(notifications)
        session.add_all(subscriptions)
        session.commit()
        
        logger.info("Test data inserted successfully")
        
    except Exception as e:
        logger.error(f"Error inserting test data: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

def setup_database():
    """Main function to set up the database."""
    try:
        # Create database
        db_url = create_database()
        
        # Create tables
        engine = create_tables(db_url)
        
        # Insert test data
        insert_test_data(engine)
        
        logger.info("Database setup completed successfully")
        
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        raise

if __name__ == "__main__":
    setup_database() 
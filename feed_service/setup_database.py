from app.utils.db_connection import Base, get_db_engine
from app.entity.feed_entity import FeedItem
from app.entity.post_entity import Post
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    try:
        # Get database engine
        engine = get_db_engine()
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Create a session
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            # Add some test posts
            logger.info("Adding test posts...")
            test_posts = [
                Post(
                    title=f"Test Post {i}",
                    content=f"This is test post content {i}",
                    user_id=10
                )
                for i in range(1, 6)
            ]
            session.bulk_save_objects(test_posts)
            session.commit()
            
            # Add feed items for user 10
            logger.info("Adding feed items...")
            feed_items = [
                FeedItem(
                    post_id=i,
                    user_id=10,
                    created_at=datetime.utcnow()
                )
                for i in range(1, 6)
            ]
            session.bulk_save_objects(feed_items)
            session.commit()
            
            logger.info("Database setup completed successfully!")
            
        except Exception as e:
            logger.error(f"Error adding test data: {e}")
            session.rollback()
            raise
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise

if __name__ == "__main__":
    setup_database() 
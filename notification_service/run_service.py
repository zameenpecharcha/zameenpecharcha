import os
import sys
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add the app directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, "app")
sys.path.append(app_dir)

from app.utils.database import SessionLocal, engine
from app.entity.notification import Base
from app.service.notification_service import NotificationServiceServicer
from app.proto_files import notification_pb2_grpc
import grpc
from concurrent import futures

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    try:
        # Drop existing tables and indexes
        with engine.connect() as connection:
            # Get all table names
            tables = Base.metadata.tables.keys()
            
            # Drop all tables
            for table in tables:
                connection.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            
            connection.commit()
            logger.info("Dropped existing tables and indexes")
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def serve():
    try:
        # Initialize database
        init_db()
        
        # Create gRPC server
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        
        # Add notification service
        db = SessionLocal()
        notification_pb2_grpc.add_NotificationServiceServicer_to_server(
            NotificationServiceServicer(db), server)
        
        # Start server
        server.add_insecure_port('localhost:50056')
        server.start()
        logger.info("Notification service started on port 50056")
        
        # Keep the server running
        server.wait_for_termination()
        
    except Exception as e:
        logger.error(f"Error starting service: {str(e)}")
        raise
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    serve() 
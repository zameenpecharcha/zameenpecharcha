import os
import sys

# Add the app directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_dir)

from .db_connection import Base, get_db_engine
from ..entity.feed_entity import FeedItem
from ..entity.post_entity import Post

def create_tables():
    engine = get_db_engine()
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables() 
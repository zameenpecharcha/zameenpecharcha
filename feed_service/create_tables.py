from app.utils.db_connection import Base, get_db_engine
from app.entity.feed_entity import FeedItem
from app.entity.post_entity import Post

def create_tables():
    engine = get_db_engine()
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables() 
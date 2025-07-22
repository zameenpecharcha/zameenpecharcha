from app.utils.db_connection import get_db_engine
from app.entity.post_entity import Post
from sqlalchemy.orm import sessionmaker

def create_test_data():
    # Create engine and session
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create a test post
        test_post = Post(
            id=10,  # Specific ID to match your request
            title="Test Post",
            content="This is a test post content",
            user_id=10  # Matching the user_id from your request
        )
        session.add(test_post)
        session.commit()
        print("Test post created successfully!")

    except Exception as e:
        print(f"Error creating test data: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_test_data() 
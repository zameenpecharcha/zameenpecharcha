from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import uuid

def migrate_to_uuid():
    # Load environment variables
    load_dotenv()
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    
    # Create database URL
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Connected to database")
        
        # Start transaction
        trans = conn.begin()
        try:
            print("Getting existing UUIDs from posts and comments...")
            # Get all unique user IDs from posts and comments
            result = conn.execute(text("""
                SELECT DISTINCT user_id::uuid FROM posts
                UNION
                SELECT DISTINCT user_id::uuid FROM comments;
            """))
            existing_uuids = [row[0] for row in result]
            
            print(f"Found {len(existing_uuids)} unique user IDs")
            
            print("Creating temporary UUID column...")
            # Add new UUID column
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN user_id_new UUID DEFAULT gen_random_uuid();
            """))
            
            # Update existing users with new UUIDs
            conn.execute(text("""
                UPDATE users
                SET user_id_new = gen_random_uuid();
            """))
            
            # For each existing UUID, create a user if it doesn't exist
            for user_uuid in existing_uuids:
                print(f"Processing UUID: {user_uuid}")
                conn.execute(text("""
                    INSERT INTO users (user_id_new, name, email, password)
                    VALUES (:uuid, :name, :email, :password)
                    ON CONFLICT DO NOTHING;
                """), {
                    "uuid": user_uuid,
                    "name": f"User {str(user_uuid)[:8]}",
                    "email": f"user_{str(user_uuid)[:8]}@example.com",
                    "password": "placeholder"
                })
            
            print("Copying data to new column...")
            # Update foreign key references in other tables
            conn.execute(text("""
                ALTER TABLE posts 
                ADD COLUMN user_id_new UUID;
            """))
            
            conn.execute(text("""
                UPDATE posts p
                SET user_id_new = p.user_id::uuid;
            """))
            
            conn.execute(text("""
                ALTER TABLE comments 
                ADD COLUMN user_id_new UUID;
            """))
            
            conn.execute(text("""
                UPDATE comments c
                SET user_id_new = c.user_id::uuid;
            """))
            
            print("Dropping old columns and constraints...")
            # Drop old columns and constraints
            conn.execute(text("ALTER TABLE posts DROP COLUMN user_id;"))
            conn.execute(text("ALTER TABLE comments DROP COLUMN user_id;"))
            conn.execute(text("ALTER TABLE users DROP COLUMN user_id;"))
            
            print("Renaming new columns...")
            # Rename new columns
            conn.execute(text("""
                ALTER TABLE users 
                RENAME COLUMN user_id_new TO user_id;
            """))
            conn.execute(text("""
                ALTER TABLE posts 
                RENAME COLUMN user_id_new TO user_id;
            """))
            conn.execute(text("""
                ALTER TABLE comments 
                RENAME COLUMN user_id_new TO user_id;
            """))
            
            print("Adding constraints...")
            # Add primary key constraint
            conn.execute(text("""
                ALTER TABLE users 
                ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);
            """))
            
            # Add foreign key constraints
            conn.execute(text("""
                ALTER TABLE posts 
                ADD CONSTRAINT posts_user_id_fkey 
                FOREIGN KEY (user_id) 
                REFERENCES users(user_id) ON DELETE CASCADE;
            """))
            
            conn.execute(text("""
                ALTER TABLE comments 
                ADD CONSTRAINT comments_user_id_fkey 
                FOREIGN KEY (user_id) 
                REFERENCES users(user_id) ON DELETE CASCADE;
            """))
            
            # Commit transaction
            trans.commit()
            print("Migration completed successfully!")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"Error during migration: {str(e)}")
            raise

if __name__ == "__main__":
    migrate_to_uuid() 
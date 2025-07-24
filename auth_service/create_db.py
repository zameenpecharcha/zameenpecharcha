from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_database():
    load_dotenv()
    
    # Get credentials from .env
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "5434")
    DB_NAME = "zameenpecharcha"
    
    print("Setting up database...")
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Create database if it doesn't exist
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
        exists = cur.fetchone()
        if not exists:
            print(f"Creating database {DB_NAME}...")
            cur.execute(f'CREATE DATABASE {DB_NAME}')
            print(f"Database {DB_NAME} created successfully!")
        else:
            print(f"Database {DB_NAME} already exists.")
        
        # Close connection to postgres database
        cur.close()
        conn.close()
        
        # Connect to the new database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Create users table if it doesn't exist
        print("Creating users table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                name VARCHAR(50),
                email VARCHAR(50) UNIQUE NOT NULL,
                phone INTEGER,
                profile_photo VARCHAR(50),
                role VARCHAR(50),
                location VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                bio VARCHAR(50),
                password VARCHAR(100) NOT NULL
            )
        """)
        print("Users table created/verified successfully!")
        
        # Close communication
        cur.close()
        conn.close()
        
        print("\nDatabase setup completed successfully!")
        
    except Exception as e:
        print(f"\nError during database setup: {str(e)}")

if __name__ == "__main__":
    setup_database() 
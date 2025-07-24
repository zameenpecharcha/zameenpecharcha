from dotenv import load_dotenv
import os
import psycopg2

def test_connection():
    load_dotenv()
    
    # Get credentials from .env
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")
    
    print("Testing with these credentials:")
    print(f"User: {DB_USER}")
    print(f"Host: {DB_HOST}")
    print(f"Port: {DB_PORT}")
    print(f"Database: {DB_NAME}")
    
    try:
        # Try to connect
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Execute a test query
        cur.execute('SELECT version();')
        
        # Fetch the result
        version = cur.fetchone()
        print("\nSuccess! Connected to PostgreSQL")
        print(f"PostgreSQL version: {version[0]}")
        
        # Close communication
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\nError connecting to database: {str(e)}")

if __name__ == "__main__":
    test_connection() 
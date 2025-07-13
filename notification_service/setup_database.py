import os
import sys

# Add the app directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, "app")
sys.path.append(app_dir)

from app.utils.setup_db import setup_database

if __name__ == "__main__":
    setup_database() 
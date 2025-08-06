import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from user_service.app.service.user_service import serve

if __name__ == "__main__":
    serve() 
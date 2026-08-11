import os

# Base directory of the backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite database file lives in backend/data/
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'memory_os.db')}"

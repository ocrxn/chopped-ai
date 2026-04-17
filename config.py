import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Base directory
if hasattr(sys, '_MEIPASS'):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Neon DB
DATABASE_URL = os.getenv('DATABASE_URL')

# Uploads & output
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
JSON_FOLDER = os.path.join(BASE_DIR, "json")
CLIPS_FOLDER = os.path.join(BASE_DIR, "clips")
ZIP_FOLDER = os.path.join(BASE_DIR, "zips")

for folder in [UPLOAD_FOLDER, JSON_FOLDER, CLIPS_FOLDER, ZIP_FOLDER]:
    os.makedirs(folder, exist_ok=True)
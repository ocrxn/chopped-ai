import os
import sys
import logging
from dotenv import load_dotenv

if hasattr(sys, '_MEIPASS'):
    env_path = os.path.join(sys._MEIPASS, '.env')
else:
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

load_dotenv(env_path)

DATABASE_URL = os.getenv('DATABASE_URL')
APP_KEY = os.getenv('APP_KEY')

if hasattr(sys, '_MEIPASS'):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.info(f"Using env_path: {env_path}")
logging.info(f"BASE_DIR: {BASE_DIR}")
logging.info(f"DATABASE_URL found: {bool(DATABASE_URL)}")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
JSON_FOLDER = os.path.join(BASE_DIR, "json")
CLIPS_FOLDER = os.path.join(BASE_DIR, "clips")
ZIP_FOLDER = os.path.join(BASE_DIR, "zips")

for folder in [UPLOAD_FOLDER, JSON_FOLDER, CLIPS_FOLDER, ZIP_FOLDER]:
    os.makedirs(folder, exist_ok=True)
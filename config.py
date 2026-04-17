import os
from dotenv import load_dotenv

load_dotenv()

#Localhost
HOST = os.getenv('HOST_TOKEN')
PORT = os.getenv('PORT_TOKEN')
USER = os.getenv('USER_TOKEN')
PASSWORD = os.getenv('PASSWORD_TOKEN')
DATABASE = os.getenv('DB_TOKEN')

#Neon DB
DB_URL = os.getenv('DATABASE_URL')

#Gmail
MAIL_TOKEN = os.getenv('mail_token')
SENDER_EMAIL = os.getenv('sender_email')
EMAIL_PORT = os.getenv('email_port')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#Uploads & output
UPLOAD_FOLDER = os.path.join(BASE_DIR, os.getenv('upload_folder'))
JSON_FOLDER = os.path.join(BASE_DIR, os.getenv('json_folder'))
CLIPS_FOLDER = os.path.join(BASE_DIR, os.getenv('clips_folder'))
ZIP_FOLDER = os.path.join(BASE_DIR, os.getenv('zip_folder'))

def init_dirs():
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(CLIPS_FOLDER, exist_ok=True)
        os.makedirs(ZIP_FOLDER, exist_ok=True)
        os.makedirs(JSON_FOLDER, exist_ok=True)
    except Exception as e:
        print(f"Exception in init_dirs: {e}")

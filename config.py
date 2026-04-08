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
CLIPS_FOLDER = os.path.join(BASE_DIR, os.getenv('clips_folder'))
ZIP_FOLDER = os.path.join(BASE_DIR, os.getenv('zip_folder'))

def init_dirs():
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            os.mkdir(UPLOAD_FOLDER)
        if not os.path.exists(CLIPS_FOLDER):
            os.mkdir(CLIPS_FOLDER)
        if not os.path.exists(ZIP_FOLDER):
            os.mkdir(ZIP_FOLDER)
    except Exception as e:
        print(f"Exception in init_dirs: {e}")

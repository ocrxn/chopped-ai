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


#Uploads
UPLOAD_FOLDER = os.getenv('upload_folder')

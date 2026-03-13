import smtplib, ssl
import getpass
import secrets
from config import MAIL_TOKEN, SENDER_EMAIL, EMAIL_PORT

port = EMAIL_PORT
smtp_server = 'smtp.gmail.com'
sender_email = SENDER_EMAIL

#Generate a six digit code
def gen_code(length=6):
    return "".join(secrets.choice("23456789") for _ in range(length))

#Connect to SMTP and send user the generated code                                                    
def connect_smtp(username, receiver_email):
    message = f"""Hello {username}
Here is your six digit code: {gen_code()}"""
    context = ssl.create_default_context()

    #Auto opens and closes secure SSL connection to SMTP to send message
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, MAIL_TOKEN)
        server.sendmail(sender_email, receiver_email, message)
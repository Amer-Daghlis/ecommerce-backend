import bcrypt
import smtplib
import random
import string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string# Hash a plain password
def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# Verify a plain password against a hashed
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_verification_code() -> str:
    return str(random.randint(100000, 999999))

def send_verification_email(email: str, code: str):
    # Email details
    subject = "Verification Code for Moedati Web"
    sender_email = "alifaqi68@gmail.com"
    receiver_email = email

    # SMTP credentials (login sender)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "alifaqi68@gmail.com"
    smtp_password = "ulxx npip xqfv hmtd"
    # alifaqi68@gmail.com
    # ulxx npip xqfv hmtd

    # Create MIME message with HTML content
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; text-align: center;">
        <h1 style="color: #2F4F4F;">Welcome in moedati!</h1>
        <h2>Safe Web Verification</h2>
        <p>Your verification code is:</p>
        <div style="font-size: 24px; font-weight: bold; color: #2F4F4F;">{code}</div>
        <p>This code will expire in 1 minute.</p>
      </body>
    </html>
    """

    message.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise
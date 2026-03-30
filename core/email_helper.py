import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.config import settings
import random

def generate_otp() -> str:
    """Generate a random 5-digit OTP."""
    return str(random.randint(10000, 99999))

def send_otp_email(to_email: str, otp: str):
    """Send OTP via Email using SMTP."""
    msg = MIMEMultipart()
    msg['From'] = settings.SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = "Farm to Plate - Email Verification OTP"
    body = f"আপনার Farm to Plate অ্যাকাউন্ট ভেরিফিকেশন কোড হচ্ছে: {otp}\nঅনুগ্রহ করে কোডটি ওয়েবসাইটে প্রদান করে অ্যাকাউন্ট সক্রিয় করুন।"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(settings.SENDER_EMAIL, settings.SENDER_EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")
        raise e

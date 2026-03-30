import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.config import settings
import traceback

def send_otp_email(receiver_email: str, otp: str):
    sender_email = settings.MAIL_SENDER
    sender_password = settings.MAIL_PASSWORD
    if not sender_password:
        print(f"Warning: MAIL_PASSWORD not found in env. OTP is {otp}")
        return
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "Krishok Platform - OTP Verification"
    message["From"] = sender_email
    message["To"] = receiver_email

    # The HTML version includes a link to open the OTP verification page directly (assuming it's running locally or domain)
    html = f"""\
    <html>
      <body>
        <h2>Verification Code</h2>
        <p>Your 5-digit verification code is: <strong>{otp}</strong></p>
        <p>Or click this link to verify directly: <a href="http://192.168.1.9:8080/opt.html?email={receiver_email}">Verify Here</a></p>
      </body>
    </html>
    """
    part = MIMEText(html, "html")
    message.attach(part)

    try:
        # Assuming Gmail is used
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
    except Exception as e:
        print("Failed to send email:", e)
        traceback.print_exc()

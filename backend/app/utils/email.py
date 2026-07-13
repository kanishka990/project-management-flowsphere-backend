import smtplib
from email.message import EmailMessage
from app.core.config import get_settings

def send_reset_password_email(email_to: str, token: str):
    settings = get_settings()
    
    # Do nothing if SMTP is not configured
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        print("SMTP credentials are not configured. Email not sent.")
        return
        
    msg = EmailMessage()
    msg['Subject'] = 'Password Reset Request - Task Orbit'
    msg['From'] = settings.SMTP_FROM_EMAIL
    msg['To'] = email_to

    # Link to your frontend application
    frontend_url = settings.FRONTEND_URL.rstrip('/')
    reset_link = f"{frontend_url}/reset-password?token={token}"
    
    msg.set_content(
        f"Hello,\n\n"
        f"You requested a password reset. Please click the link below to reset your password:\n\n"
        f"{reset_link}\n\n"
        f"If you did not request this, please ignore this email."
    )

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            # Some company internal SMTPs do not require TLS
            if settings.SMTP_PORT != 25:
                server.starttls()  # Secure the connection
            
            # Internal company SMTPs often use IP whitelisting instead of auth
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

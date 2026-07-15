import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from app.core.config import get_settings


DEFAULT_FRONTEND_URL = "http://localhost:5173"


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _looks_like_email(value: str | None) -> bool:
    return bool(value and "@" in value)


def _frontend_url() -> str:
    settings = get_settings()
    return (_clean(settings.FRONTEND_URL) or DEFAULT_FRONTEND_URL).rstrip("/")


def _sender_header(smtp_host: str | None) -> str | None:
    settings = get_settings()
    from_email = _clean(settings.SMTP_FROM_EMAIL)
    if not from_email:
        return None

    display_name = _clean(settings.SMTP_USER)
    if smtp_host and smtp_host.lower() == "smtp.gmail.com" and display_name and not _looks_like_email(display_name):
        return formataddr((display_name, from_email))
    return from_email


def _auth_username(smtp_host: str | None) -> str | None:
    settings = get_settings()
    smtp_user = _clean(settings.SMTP_USER)
    if smtp_host and smtp_host.lower() == "smtp.gmail.com" and not _looks_like_email(smtp_user):
        return _clean(settings.SMTP_FROM_EMAIL)
    return smtp_user or _clean(settings.SMTP_FROM_EMAIL)


def _send_email(email_to: str, subject: str, body: str) -> None:
    settings = get_settings()
    smtp_host = _clean(settings.SMTP_HOST)
    smtp_port = settings.SMTP_PORT or 587
    sender = _sender_header(smtp_host)

    if not smtp_host or not sender:
        print("SMTP host/from email are not configured. Email not sent.")
        return

    auth_username = _auth_username(smtp_host)
    smtp_password = _clean(settings.SMTP_PASSWORD)
    gmail_host_requires_auth = smtp_host.lower() == "smtp.gmail.com"

    if gmail_host_requires_auth and (not auth_username or not smtp_password):
        print("Gmail SMTP username/password are not configured. Email not sent.")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = email_to
    msg.set_content(body)

    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                if auth_username and smtp_password:
                    server.login(auth_username, smtp_password)
                server.send_message(msg)
            return

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if smtp_port != 25:
                server.starttls()

            if auth_username and smtp_password:
                server.login(auth_username, smtp_password)

            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")


def send_reset_password_email(email_to: str, token: str):
    frontend_url = _frontend_url()
    reset_link = f"{frontend_url}/reset-password?token={token}"

    _send_email(
        email_to=email_to,
        subject="Password Reset Request - Task Orbit",
        body=(
            f"Hello,\n\n"
            f"You requested a password reset. Please click the link below to reset your password:\n\n"
            f"{reset_link}\n\n"
            f"If you did not request this, please ignore this email."
        ),
    )


def send_verification_email(email_to: str, token: str):
    frontend_url = _frontend_url()
    verification_link = f"{frontend_url}/verify-email?token={token}"

    _send_email(
        email_to=email_to,
        subject="Verify Your Email - Task Orbit",
        body=(
            f"Hello,\n\n"
            f"Thank you for registering with Task Orbit. Please verify your email address "
            f"by clicking the link below:\n\n"
            f"{verification_link}\n\n"
            f"This verification link expires in 24 hours.\n\n"
            f"If you did not create this account, please ignore this email."
        ),
    )

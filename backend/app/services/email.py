import logging
import smtplib
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.services.system_settings import get_smtp_settings

logger = logging.getLogger("beeboard.email")


def send_registration_email(db: Session, recipient_email: str, username: str) -> bool:
    smtp = get_smtp_settings(db)
    if not smtp.get("configured"):
        return False

    host = smtp.get("host")
    port = smtp.get("port")
    from_email = smtp.get("from_email")
    if not host or not port or not from_email:
        return False

    msg = EmailMessage()
    msg["Subject"] = "Willkommen bei BeeBoard"
    msg["From"] = from_email
    msg["To"] = recipient_email
    msg.set_content(
        f"Hallo {username},\n\n"
        "dein Konto bei BeeBoard wurde erfolgreich erstellt.\n"
        "Du kannst dich jetzt in der App anmelden.\n\n"
        "Viele Gruesse\n"
        "Dein BeeBoard-Team"
    )

    try:
        if smtp.get("use_ssl"):
            server = smtplib.SMTP_SSL(host=host, port=int(port), timeout=10)
        else:
            server = smtplib.SMTP(host=host, port=int(port), timeout=10)

        with server:
            if smtp.get("use_tls") and not smtp.get("use_ssl"):
                server.starttls()

            username_cfg = smtp.get("username")
            password_cfg = smtp.get("password")
            if username_cfg and password_cfg:
                server.login(username_cfg, password_cfg)

            server.send_message(msg)
        return True
    except Exception as exc:
        logger.warning("Registration email could not be sent: %s", exc)
        return False

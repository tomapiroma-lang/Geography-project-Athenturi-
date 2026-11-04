import smtplib
from email.message import EmailMessage

from flask import current_app


def notify(subject, body, reply_to=None):
    """Email the site owner. Returns False quietly when mail is not configured."""
    c = current_app.config
    if not (c["MAIL_HOST"] and c["MAIL_TO"]):
        return False
    msg = EmailMessage()
    msg["Subject"], msg["To"] = subject, c["MAIL_TO"]
    msg["From"] = c["MAIL_USER"] or c["MAIL_TO"]
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(body)
    try:
        with smtplib.SMTP(c["MAIL_HOST"], c["MAIL_PORT"], timeout=10) as s:
            s.starttls()
            if c["MAIL_USER"]:
                s.login(c["MAIL_USER"], c["MAIL_PASS"])
            s.send_message(msg)
        return True
    except (OSError, smtplib.SMTPException):
        return False

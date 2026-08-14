"""OTP / notification delivery.

Emails are sent via SMTP when configured; otherwise (or for SMS) the code is
logged to the console so the app works end-to-end in development.
"""

from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..config import settings


def send_otp_email(to_email: str, code: str) -> bool:
    if not settings.smtp_host:
        print(f"[STAYSYNC-OTP-EMAIL] {to_email} -> {code}")
        return False
    try:
        msg = MIMEMultipart()
        msg["From"] = settings.mail_from
        msg["To"] = to_email
        msg["Subject"] = "Your StaySync verification code"
        msg.attach(MIMEText(
            f"Your StaySync OTP is: {code}\n\n"
            f"It is valid for {settings.otp_expire_minutes} minutes. "
            "Never share it with anyone.\n\n- The StaySync Team", "plain"
        ))
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.mail_from, [to_email], msg.as_string())
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[STAYSYNC-OTP-EMAIL-FAILED] {exc}")
        return False


def send_otp_sms(phone: str, code: str) -> bool:
    # TODO: wire an SMS gateway (Twilio, MSG91, AWS SNS, ...) for production.
    print(f"[STAYSYNC-OTP-SMS] {phone} -> {code}")
    return False


def send_otp(identifier: str, code: str) -> dict:
    is_email = "@" in identifier
    delivered = send_otp_email(identifier, code) if is_email else send_otp_sms(identifier, code)
    return {"delivered": delivered, "channel": "email" if is_email else "sms"}

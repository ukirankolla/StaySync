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


def send_welcome_email(to_email: str, full_name: str = "") -> bool:
    """Thank-you / onboarding email sent on first-time signup."""
    if not settings.smtp_host:
        print(f"[STAYSYNC-WELCOME-EMAIL] {to_email} ({full_name or 'no name'})")
        return False
    name = full_name or "there"
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = settings.mail_from
        msg["To"] = to_email
        msg["Subject"] = "Welcome to StaySync — let's find your roommates"
        text = (
            f"Hi {name},\n\n"
            "Thanks for signing up with StaySync! We're glad you're here.\n\n"
            "What to do next:\n"
            "1. Complete your profile (city, budget, move-in date).\n"
            "2. Answer the short lifestyle questionnaire for accurate match scores.\n"
            "3. Browse recommendations and connect with compatible people.\n"
            "4. Find a flat that fits your group.\n\n"
            "Need help? Just reply to this email.\n\n"
            "- The StaySync Team"
        )
        html = (
            '<html><body style="font-family:Arial,Helvetica,sans-serif;background:#f6f7fb;padding:24px">'
            '<div style="max-width:560px;margin:auto;background:#ffffff;border-radius:14px;overflow:hidden;'
            'border:1px solid #e2e8f0">'
            '<div style="background:#4f46e5;color:#fff;padding:24px;text-align:center">'
            '<h2 style="margin:0">Welcome to StaySync</h2></div>'
            '<div style="padding:28px;color:#1e293b">'
            f"<p>Hi {name},</p>"
            "<p>Thanks for signing up! We're excited to help you find a roommate who actually fits.</p>"
            "<p>What to do next:</p><ol>"
            "<li>Complete your profile (city, budget, move-in date).</li>"
            "<li>Answer the short lifestyle questionnaire for accurate match scores.</li>"
            "<li>Browse recommendations and connect with compatible people.</li>"
            "<li>Find a flat that fits your group.</li></ol>"
            '<p style="color:#64748b">Need help? Reply to this email anytime.</p></div>'
            '<div style="background:#eef2ff;color:#4f46e5;padding:14px;text-align:center;font-size:13px">'
            "StaySync — find compatible roommates before you move</div>"
            "</div></body></html>"
        )
        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.mail_from, [to_email], msg.as_string())
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[STAYSYNC-WELCOME-EMAIL-FAILED] {exc}")
        return False

"""OTP / notification delivery.

Emails are delivered via the Brevo HTTPS API when BREVO_API_KEY is configured
(preferred: Railway allows outbound web traffic on all plans). Otherwise they
fall back to SMTP, and finally to console logging so the app works in dev.
"""

from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx

from ..config import settings

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def _send_brevo(to_email: str, subject: str, text: str, html: str = "") -> bool:
    if not settings.brevo_api_key:
        return False
    payload = {
        "sender": {"name": settings.sender_name, "email": settings.sender_email},
        "to": [{"email": to_email, "name": to_email}],
        "subject": subject,
        "textContent": text,
    }
    if html:
        payload["htmlContent"] = html
    try:
        resp = httpx.post(
            BREVO_URL,
            json=payload,
            headers={"api-key": settings.brevo_api_key, "accept": "application/json"},
            timeout=20,
        )
        if resp.status_code in (200, 201, 202):
            return True
        print(f"[STAYSYNC-EMAIL-API-FAILED] status={resp.status_code} body={resp.text[:300]}")
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"[STAYSYNC-EMAIL-API-FAILED] {exc}")
        return False


def _send_smtp(to_email: str, subject: str, text: str, html: str = "") -> bool:
    if not settings.smtp_host:
        return False
    try:
        msg = MIMEMultipart("alternative" if html else "mixed")
        msg["From"] = settings.mail_from
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(text, "plain"))
        if html:
            msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=3) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.mail_from, [to_email], msg.as_string())
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[STAYSYNC-EMAIL-SMTP-FAILED] {exc}")
        return False


def _send_email(to_email: str, subject: str, text: str, html: str = "") -> bool:
    if _send_brevo(to_email, subject, text, html):
        return True
    if _send_smtp(to_email, subject, text, html):
        return True
    print(f"[STAYSYNC-EMAIL-CONSOLE] {to_email} -> {subject}")
    return False


def send_otp_email(to_email: str, code: str) -> bool:
    subject = "Your StaySync verification code"
    text = (
        f"Your StaySync OTP is: {code}\n\n"
        f"It is valid for {settings.otp_expire_minutes} minutes. "
        "Never share it with anyone.\n\n- The StaySync Team"
    )
    return _send_email(to_email, subject, text)


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
    name = full_name or "there"
    subject = "Welcome to StaySync — let's find your roommates"
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
    return _send_email(to_email, subject, text, html)

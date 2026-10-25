import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def send_signup_otp_email(user, plain_otp: str) -> bool:
    """
    Sends the 6-digit signup OTP using Brevo Transactional Email API.
    If BREVO_API_KEY is not configured, logs to console for local testing.
    """
    api_key = getattr(settings, 'BREVO_API_KEY', '').strip()
    sender_email = getattr(settings, 'BREVO_SENDER_EMAIL', 'noreply@sarkarisaathi.org')
    sender_name = getattr(settings, 'BREVO_SENDER_NAME', 'Sarkari Saathi')

    subject = f"Your Sarkari Saathi Verification Code: {plain_otp}"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #F7F4EE; color: #131E29; margin: 0; padding: 24px; }}
            .container {{ max-width: 560px; margin: 0 auto; background: #FFFFFF; border: 2px solid #131E29; padding: 32px; border-radius: 4px; }}
            .header {{ border-bottom: 2px solid #131E29; padding-bottom: 16px; margin-bottom: 24px; }}
            .title {{ font-size: 24px; font-weight: bold; margin: 0; color: #131E29; }}
            .otp-box {{ background: #F9F6F0; border: 2px dashed #BA1A1A; padding: 20px; text-align: center; margin: 28px 0; }}
            .otp-code {{ font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #BA1A1A; font-family: monospace; }}
            .warning {{ font-size: 14px; color: #52606D; margin-top: 24px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="title">Sarkari Saathi</h1>
                <p style="margin: 4px 0 0 0; color: #52606D;">Your citizen guide to government forms</p>
            </div>
            <p>Namaste <strong>{user.name}</strong>,</p>
            <p>Use the 6-digit verification code below to verify your email and activate your account:</p>
            <div class="otp-box">
                <div class="otp-code">{plain_otp}</div>
                <p style="margin: 8px 0 0 0; font-size: 13px; color: #52606D;">Valid for 10 minutes</p>
            </div>
            <p class="warning">
                <strong>Safety Notice:</strong> Never share this OTP with anyone. Sarkari Saathi will never call or message asking for your password, Aadhaar, or government portal credentials.
            </p>
        </div>
    </body>
    </html>
    """

    if not api_key:
        logger.info(f"==> [LOCAL DEV / BREVO MOCK] OTP for {user.email} is: {plain_otp}")
        print(f"\n=======================================================")
        print(f" [SARKARI SAATHI] SIGNUP OTP FOR {user.email}: {plain_otp}")
        print(f"=======================================================\n")
        return True

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }
    payload = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": user.email, "name": user.name}],
        "subject": subject,
        "htmlContent": html_content
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in (200, 201, 202):
            return True
        logger.error(f"Brevo API error: {response.status_code} - {response.text}")
        return False
    except Exception as e:
        logger.exception(f"Failed to send email via Brevo: {e}")
        return False

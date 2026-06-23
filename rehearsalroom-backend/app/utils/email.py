import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


def send_invitation_email(invited_email: str, band_name: str, inviter_name: str, token: str) -> bool:
    """
    Send invitation email. Returns True on success, False on failure.
    This is a stub — configure SMTP credentials in .env to enable real email sending.
    """
    accept_url = f"{settings.FRONTEND_URL}/invitations/accept?token={token}"

    subject = f"You're invited to join {band_name} on RehearsalRoom!"
    body_html = f"""
    <html>
    <body>
        <h2>Band Invitation</h2>
        <p>Hi there!</p>
        <p><strong>{inviter_name}</strong> has invited you to join the band 
        <strong>{band_name}</strong> on RehearsalRoom.</p>
        <p>Click the link below to accept the invitation:</p>
        <p><a href="{accept_url}" style="
            background-color: #6366f1; 
            color: white; 
            padding: 12px 24px; 
            text-decoration: none; 
            border-radius: 6px;
            display: inline-block;
        ">Accept Invitation</a></p>
        <p>Or copy this link: {accept_url}</p>
        <p><small>This invitation will expire in 7 days.</small></p>
        <br>
        <p>— The RehearsalRoom Team</p>
    </body>
    </html>
    """

    # If SMTP not configured, just log and return True (dev mode)
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"[EMAIL STUB] Invitation to {invited_email}: {accept_url}")
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        msg["To"] = invited_email

        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM_EMAIL, invited_email, msg.as_string())

        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send to {invited_email}: {e}")
        return False

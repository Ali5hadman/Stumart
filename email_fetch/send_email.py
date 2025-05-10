import smtplib
from email.message import EmailMessage
import json

def send_email_smtp(
    subject: str,
    body: str,
    to_addrs: list[str],
    cc_addrs: list[str] | None = None,
    bcc_addrs: list[str] | None = None,
):
    """
    Send an email via SMTP.
    - smtp_host, smtp_port: your SMTP server (e.g. 'smtp.gmail.com', 465)
    - smtp_user, smtp_pass: your login credentials (for Gmail, use an App Password)
    - subject, body: message headers & text
    - from_addr: sender address
    - to_addrs, cc_addrs, bcc_addrs: recipient lists
    """

    # Load config
    with open('smtp_config.json', 'r', encoding='utf-8') as f:
        cfg = json.load(f)['smtp']
        
    smtp_host=cfg['host']
    smtp_port=cfg['port']
    smtp_user=cfg['user']
    smtp_pass=cfg['password']
    from_addr = cfg['user']

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = from_addr
    msg["To"]      = ", ".join(to_addrs)
    if cc_addrs:
        msg["Cc"] = ", ".join(cc_addrs)
    # Note: Bcc isn’t a header; it just gets added to the send list below
    
    msg.set_content(body)

    # build full recipient list
    recipients = to_addrs + (cc_addrs or []) + (bcc_addrs or [])

    # connect and send
    with smtplib.SMTP_SSL(smtp_host, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg, from_addr=from_addr, to_addrs=recipients)
        print(f"Email sent to: {recipients}")



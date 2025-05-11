import imaplib
import mailbox
import email
import os
import json

from email.header import decode_header, make_header
import base64
import json




def mbox_to_json(mbox_path):
    """
    Read an MBOX file and return its contents as a JSON string:
    [
      {
        "from": "...",
        "to": [...],
        "cc": [...],
        "bcc": [...],
        "date": "...",
        "subject": "...",
        "body": "...",          # plain-text body (first text/plain part)
        "attachments": [        # list of {"filename": "...", "content_type": "...", "data_base64": "..."}
          { ... }, ...
        ]
      },
      ...
    ]
    """
    messages = []
    # mbox = mailbox.mbox(mbox_path)
    mbox = mbox_path

    for msg in mbox:
        # Decode headers
        def decode(hdr):
            raw = msg.get(hdr, '')
            return str(make_header(decode_header(raw)))

        record = {
            "from":    decode('From'),
            "to":      [a.strip() for a in msg.get_all('To', [])],
            "cc":      [a.strip() for a in msg.get_all('Cc', [])],
            "bcc":     [a.strip() for a in msg.get_all('Bcc', [])],
            "date":    decode('Date'),
            "subject": decode('Subject'),
            "body":    None,
            "attachments": []
        }

        # Walk through the payload
        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = part.get("Content-Disposition", "").lower()
                ct = part.get_content_type()

                # attachments
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    payload = part.get_payload(decode=True) or b""
                    record["attachments"].append({
                        "filename": filename or "",
                        "content_type": ct,
                        "data_base64": base64.b64encode(payload).decode("ascii")
                    })

                # first text/plain part as body
                elif ct == "text/plain" and record["body"] is None:
                    charset = part.get_content_charset() or "utf-8"
                    text = part.get_payload(decode=True).decode(charset, errors="replace")
                    record["body"] = text.strip()

        else:
            # not multipart: use payload as body
            charset = msg.get_content_charset() or "utf-8"
            record["body"] = msg.get_payload(decode=True).decode(charset, errors="replace").strip()

        messages.append(record)

    # return pretty-printed JSON
    return json.dumps(messages, ensure_ascii=False, indent=2)




def fetch_email(num_email = 2):

    # Load config
    with open('smtp_config.json', 'r', encoding='utf-8') as f:
        cfg = json.load(f)['smtp']
        

    # 1. IMAP connection settings
    IMAP_HOST = cfg['host']
    IMAP_USER = cfg['user']
    IMAP_PASS = cfg['password']

    # 2. Connect & login
    M = imaplib.IMAP4_SSL(IMAP_HOST)
    M.login(IMAP_USER, IMAP_PASS)

    # 3. Select the folder you want to export
    M.select('INBOX')

    # 4. Search for all messages, then pick only the last two IDs
    typ, msg_nums = M.search(None, 'ALL')
    if typ != 'OK':
        raise RuntimeError("Failed to search mailbox")

    all_ids = msg_nums[0].split()            # e.g. [b'1', b'2', ..., b'150']
    last_two = all_ids[-num_email:]                  # keep only the last two

    # 5. Open (or create) your target mbox file
    mbox = mailbox.mbox('misc.mbox')
    mbox.lock()

    # 6. Fetch & append each of the last two messages
    for num in last_two:
        typ, data = M.fetch(num, '(RFC822)')
        if typ != 'OK':
            print(f"Warning: could not fetch message {num}")
            continue

        raw = data[0][1]
        msg = email.message_from_bytes(raw)
        mbox.add(msg)

    
    # Convert the mbox to JSON
    mailJson = mbox_to_json(mbox)
    
    mbox_path = 'misc.mbox'

    # 7. Clean up
    mbox.flush()
    mbox.unlock()
    mbox.close()
    M.logout()
    os.remove(mbox_path)

    return mailJson

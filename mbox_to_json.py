import mailbox
import email
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


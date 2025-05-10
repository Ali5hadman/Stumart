import imaplib
import mailbox
import email
import os
from mbox_to_json  import mbox_to_json
import json

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

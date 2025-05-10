import imaplib
import mailbox
import email
import os

def fetch_email(num_email = 2):

    # 1. IMAP connection settings
    IMAP_HOST = 'imap.gmail.com'
    IMAP_USER = 'freecolab2023@gmail.com'
    IMAP_PASS = 'khsf rvqs zlxy lvdc'

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

    # 7. Clean up
    mbox.flush()
    mbox.unlock()
    mbox.close()
    M.logout()

    mbox = mailbox.mbox('misc.mbox')
    return mbox

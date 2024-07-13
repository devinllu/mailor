import email
from email.policy import default

import imaplib
import os
from dotenv import load_dotenv

load_dotenv()

IMAP_SERVER = 'imap.shaw.ca'
EMAIL_FOLDER = "INBOX"

USERNAME = os.getenv('EMAIL_USERNAME')
PASSWORD = os.getenv('EMAIL_PASSWORD')
OUTPUT_PATH = os.getenv('LOCAL_DOWNLOAD_PATH')

def login(server, username, password):
    obj = imaplib.IMAP4_SSL(server)
    obj.login(username, password)

    return obj

def record_email(path, message_id, content):
    print("Writing message "), message_id
    f = open('%s/%s.eml' %(path, message_id), 'wb')
    f.write(content)
    f.close()

def process_mailbox(imap_obj):

    response, body = imap_obj.search(None, "ALL")
    if response != 'OK':
        print("No messages found!")
        return

    for message_id in body[0].split():
        response, data = imap_obj.fetch(message_id, '(RFC822)')
        if response != 'OK':
            print("ERROR getting message"), message_id
            return

        record_email(OUTPUT_PATH, message_id, data[0][1])

def main():
    imap_obj = login(IMAP_SERVER, USERNAME, PASSWORD)
    response, _ = imap_obj.select(EMAIL_FOLDER)

    if response == 'OK':
        print("Processing mailbox: "), EMAIL_FOLDER
        process_mailbox(imap_obj)
        imap_obj.close()
    else:
        print(f"ERROR: Unable to open mailbox\n{response}")
    imap_obj.logout()

if __name__ == "__main__":
    main()
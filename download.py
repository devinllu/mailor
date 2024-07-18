import email
from email.policy import default
import logging

import imaplib
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

IMAP_SERVER = 'imap.shaw.ca'
# IMAP_SERVER = 'outlook.office365.com'
EMAIL_FOLDER = "INBOX"

USERNAME = os.getenv('EMAIL_USERNAME')
PASSWORD = os.getenv('EMAIL_PASSWORD')
OUTPUT_PATH = os.getenv('LOCAL_DOWNLOAD_PATH')

def login(server, username, password):
    obj = imaplib.IMAP4_SSL(server)
    obj.login(username, password)

    return obj

def record_email(path, message_id, content, title):
    print("Writing message "), message_id
    f = open(f'{path}/{title}.eml', 'wb')
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
        
        email_msg = email.message_from_bytes(data[0][1], policy=default)
        subject = str(email_msg['Subject'])

        try:
            record_email(OUTPUT_PATH, message_id, data[0][1], subject)
        except FileNotFoundError as fnfe:
            logging.error(f"File not found {fnfe}")
            logging.error(f"Ensure the path is correct: {os.path.abspath(OUTPUT_PATH)}")
        except Exception as e:
            logging.error(f"Error occurred when recording email: {e}")

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
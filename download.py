import imaplib
import os
import logging
import email

from email.policy import default
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# available tested servers: imap.shaw.ca, imap.gmail.com
IMAP_SERVER = 'imap.shaw.ca'
EMAIL_FOLDER = "INBOX"

USERNAME = os.getenv('EMAIL_USERNAME')
PASSWORD = os.getenv('EMAIL_PASSWORD')
OUTPUT_PATH = os.getenv('LOCAL_DOWNLOAD_PATH')
ERROR_LOG_PATH = os.getenv('ERROR_LOG_FILE')

def login(server, username, password):
    obj = imaplib.IMAP4_SSL(server)
    obj.login(username, password)

    return obj

def record_email(path, message_id, content, title):
    print("Writing message "), message_id
    f = open(f'{path}/{title}.eml', 'wb')
    f.write(content)
    f.close()

def log_error_message(error_msg, date, subject):
    with open(ERROR_LOG_PATH, 'a') as error_file:
        error_file.write(f'{date}\n{error_msg}\nCould not download email:{subject}\n\n\n\n\n')

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
        date = str(email_msg['Date'])

        try:
            record_email(OUTPUT_PATH, message_id, data[0][1], subject)
        except FileNotFoundError as fnfe:
            logging.error(f"File not found {fnfe}")
            logging.error(f"Ensure the path is correct: {os.path.abspath(OUTPUT_PATH)}")
            log_error_message(str(fnfe), date, subject)
        except Exception as e:
            logging.error(f"Error occurred when recording email: {e}")
            log_error_message(str(e), date, subject)

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
import email
from imapclient import IMAPClient
import logging

#instantiate custom logger
LOGGER = logging.getLogger("logger")

def get_attachments(email_msg):
    return [part.get_filename() for part in email_msg.iter_attachments()]

#method to parse mail
def parse_msgs(connection,msg_uids):
    for msg_uid,data in connection.fetch(msg_uids,"RFC822"):
        try:
            email_msg = email.message_from_bytes(data[b"RFC822"],_class=email.message.EmailMessage)
            email_subject = email_msg.get("Subject")
            email_attachments = get_attachments(email_msg)
            LOGGER.info(f"UID: {msg_uid} Subject: {email_subject} Attachments: {email_attachments}")
        except Exception as e:
            LOGGER.error(f"Failed parsing message UID: {msg_uid}: {e}")
            pass

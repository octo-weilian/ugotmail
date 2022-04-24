import email
from imapclient import IMAPClient
import logging
from email.generator import BytesGenerator
from .logginghandler import LOGGER

def get_attachments(email_msg):
    return [part.get_filename() for part in email_msg.iter_attachments()]

#method to parse mail
def parse_msgs(connection,msg_uids):
    LOGGER.info(f'Parsing {len(msg_uids)} new messages')
    for msg_uid,data in connection.fetch(msg_uids,"RFC822").items():
        try:
            email_msg = email.message_from_bytes(data[b'RFC822'],_class=email.message.EmailMessage)
            email_subject = email_msg.get("Subject")
            with open(f"data/{msg_uid} {email_subject}.eml",'wb') as dst:
                BytesGenerator(dst).flatten(email_msg)
        except Exception as e:
            LOGGER.error(f"Failed parsing message: {msg_uid}")
            pass

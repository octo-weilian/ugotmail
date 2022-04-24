import email
import logging
from imapclient import IMAPClient
from email.generator import BytesGenerator
from .logginghandler import LOGGER
import os

def get_attachments(email_msg,save_to=None):
    fnames = []
    for part in email_msg.iter_attachments():
        fname = part.get_filename()
        fnames.append(fname)
        
        if save_to and os.path.exists(save_to):
            with open(fname,'wb') as dst:
                dst.write(part.get_payload(decode=True))
    return fnames

def download_eml(email_msg,save_to=None):
    if save_to and os.path.exists(save_to):
        outf = os.path.join(save_to,f"{email_msg.get('Subject')}.eml")
        with open(outf,'wb') as dst:
            BytesGenerator(dst).flatten(email_msg)

#method to parse mail
def parse_msgs(connection,msg_uids):
    LOGGER.info(f'Parsing {len(msg_uids)} new messages')
    for msg_uid,data in connection.fetch(msg_uids,"RFC822").items():
        try:
            email_msg = email.message_from_bytes(data[b'RFC822'],_class=email.message.EmailMessage)
            email_subject = email_msg.get("Subject")
            email_attachments = get_attachments(email_msg)

        except Exception as e:
            LOGGER.error(f"Failed parsing message: {msg_uid}:{e}")
            pass

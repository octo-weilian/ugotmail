from . import *
import email
from email.generator import BytesGenerator
from email import utils
from email.message import EmailMessage

def get_attachments(email_msg,save_to=None):
    fnames = []
    for part in email_msg.iter_attachments():
        fname = part.get_filename()
        fnames.append(fname)
        
        if save_to and os.path.exists(save_to):
            outf = os.path.join(save_to,fname)
            with open(fname,'wb') as dst:
                dst.write(part.get_payload(decode=True))
    return fnames

def download_eml(email_msg,save_to=None):
    if save_to and os.path.exists(save_to):
        outf = os.path.join(save_to,f"{email_msg.get('Subject')}.eml")
        with open(outf,'wb') as dst:
            BytesGenerator(dst).flatten(email_msg)

def get_localtime(datestring):
    return utils.parsedate_to_datetime(datestring).astimezone()
    
#method to parse mail
def parse_msgs(connection,msg_uids):
    LOGGER.info(f'Parsing {len(msg_uids)} new messages')
    for msg_uid,data in connection.fetch(msg_uids,"RFC822").items():
        try:
            email_msg = email.message_from_bytes(data[b'RFC822'],_class=EmailMessage)
            email_subject = email_msg.get("Subject")
            #localtime = get_localtime(email_msg.get("Date"))
            LOGGER.info(f'Subject: {email_subject}')

        except Exception as e:
            LOGGER.error(f"Failed parsing message: {msg_uid}:{e}")
            pass

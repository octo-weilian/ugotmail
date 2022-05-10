from . import *
import email
from email import utils
from email.generator import BytesGenerator
from email.message import EmailMessage

def get_attachments(email_msg,save_to=None):
    fnames = []
    for part in email_msg.iter_attachments():
        fname = part.get_filename()
        fnames.append(fname)
        
        try:
            outf = os.path.join(save_to,fname)
            with open(fname,'wb') as dst:
                dst.write(part.get_payload(decode=True))
        except:
            LOGGER.error(f"Unable to save attachment: {save_to}")
    return fnames

def to_eml(email_msg,save_to=None):
    try:
        outf = os.path.join(save_to,f"{email_msg.get('Subject')}.eml")
        with open(outf,'wb') as dst:
            BytesGenerator(dst).flatten(email_msg)
    except Exception as e:
        LOGGER.error(f"Unable to save to eml file: {e}")

def get_localtime(datestring):
    return utils.parsedate_to_datetime(datestring)
    
#method to parse mail
def parse_msgs(connection,msg_uids):
    LOGGER.info(f'Parsing {len(msg_uids)} messages')
    for msg_uid,data in connection.fetch(msg_uids,"RFC822").items():
        email_msg = email.message_from_bytes(data[b'RFC822'],_class=EmailMessage)
        email_subject = email_msg.get("Subject")
        email_dt = get_localtime(email_msg.get("Date"))

        print([msg_uid,email_subject,email_dt])

 

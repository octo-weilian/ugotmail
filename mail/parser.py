from . import *
import email
from email import utils,policy
from email.generator import BytesGenerator
from email.message import EmailMessage
from .string_search import get_perceelnr_units_from_txt,get_nr_from_string,format_fname, string_to_perceelnr

#method to parse mail
class Parser:
    def __init__(self,connection,msg_uids):
        self.connection = connection
        self.msg_uids = msg_uids

    def parse_msgs(self,files_to=None,eml_to=None):
        for msg_uid,data in self.connection.fetch(self.msg_uids,"RFC822").items():
            msg_obj = email.message_from_bytes(data[b'RFC822'],_class=EmailMessage,policy=policy.default)
            msg_sub = msg_obj.get("Subject")
            msg_dt = self.get_timestamp(msg_obj.get("Date"))
            msg_to = utils.parseaddr(msg_obj.get("To"))[-1]

            yield {"subject":msg_sub,"received":msg_dt,"to":msg_to,"msg":msg_obj}

    @staticmethod
    def get_timestamp(datestring):
        dt = utils.parsedate_to_datetime(datestring).astimezone()
        return dt.strftime("%y-%m-%d %H:%M:%S")

    @staticmethod
    def save_eml(email_msg,fname,save_to=None):

        try:
            if os.path.exists(save_to) and fname.endswith(".eml"):
                outf = os.path.join(save_to,fname)
                with open(outf,'wb') as dst:
                    BytesGenerator(dst).flatten(email_msg)
        except Exception as e:
            LOGGER.error(f"Unable to save to eml file: {e}")

    @staticmethod
    def get_files(email_msg):
        fnames = {}
        for part in email_msg.iter_attachments():
            fname = part.get_filename()
            fnames[fname] = part
        return fnames

class ExtraParsers(Parser):
    def __init__(self,connection,msg_uids,eml_to=None,files_to=None):
        super().__init__(connection,msg_uids)
        self.eml_to = eml_to
        self.files_to = files_to

    def parse_posts(self):

        bad_records = []
        good_records = []
        for record in self.parse_msgs():
            try:
                msg_files = self.get_files(record.get("msg"))
                
                if "splitsing" in record.get("to") :
                    txt_file = next(k for (k,v) in msg_files.items() if k.endswith(".txt"))
                    txt_string = msg_files.get(txt_file).get_payload(decode=True).decode("utf-8").lower()
                    msg_perceelnr,msg_units = get_perceelnr_units_from_txt(txt_string)
                    msg_nr = get_nr_from_string(txt_file,1,10)

                elif "verificatie" in record.get("to"):
                    zip_file = next(k for (k,v) in msg_files.items() if k.endswith(".zip"))
                    msg_perceelnr = string_to_perceelnr(zip_file)
                    msg_units = get_nr_from_string(record.get("subject"),1,2,True)
                    msg_nr = get_nr_from_string(record.get("subject"),6,6,True)
                    if len(str(msg_nr))<3:
                        msg_nr = None

                if self.eml_to:
                    self.save_eml(record.pop('msg'),format_fname(record.get('subject')),self.eml_to)
                else:
                    record.pop('msg')

                record["files"] = ";".join(msg_files.keys())
                record = record|{'nr':msg_nr,'perceel':msg_perceelnr,'units':msg_units}

                record[record.get("subject")] = list(record.values())
                good_records.append(record)
                
            except Exception as e:
                bad_records.append(record.get("subject"))
            
        if bad_records:
            LOGGER.error(f"Unable to parse : {bad_records}")

        return good_records



    

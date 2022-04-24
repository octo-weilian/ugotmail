import email
import threading
from urllib import response
from mail.client import Mail
import keyring
import email
from email.generator import BytesGenerator
import re
import json
# from mail import parser
import re

# outlook_inbox = Mail("outlook.office365.com",
#                         keyring.get_credential("HOTMAIL",None).username,
#                         keyring.get_credential("HOTMAIL",None).password)

# icloud_inbox = Mail("imap.mail.me.com",
#                         keyring.get_credential("APPLE",None).username,
#                         keyring.get_credential("APPLE",None).password)


# msg_uids = icloud_inbox.parse_uids()


def normalize_subject(subject):
    pattern = '\A(?!(?:COM[0-9]|CON|LPT[0-9]|NUL|PRN|AUX|com[0-9]|con|lpt[0-9]|nul|prn|aux)|[\s\.])[^\\\/:*"?<>|]{1,254}'
    result = re.sub(pattern, '_', subject)
    return result

test = 'D16073_orphan_reads.fa;710[F9|R21],14892_orphan_reads.fa;229[F19|R16]'

print(normalize_subject(test))
   

import email
import threading
from urllib import response
from mail.client import Mail
import keyring
import email
from email.generator import BytesGenerator
import re
import json
from mail import parser
import re

outlook_inbox = Mail("outlook.office365.com",
                        keyring.get_credential("HOTMAIL",None).username,
                        keyring.get_credential("HOTMAIL",None).password)


with outlook_inbox.connection() as conn:
    uids = conn.search("ALL")
    parser.parse_msgs(conn,[uids[-1]])





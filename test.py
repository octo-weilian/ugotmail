import email
from urllib import response
from mail.client import Mail
import keyring
import email
import re

outlook_client = Mail("outlook.office365.com",993,
                            keyring.get_credential("HOTMAIL",None).username,
                            keyring.get_credential("HOTMAIL",None).password)

icloud_client = Mail("imap.mail.me.com",993,
                    keyring.get_credential("APPLE",None).username,
                    keyring.get_credential("APPLE",None).password)

# with outlook_client.connection() as conn:
#     inbox = conn.select_folder("INBOX",readonly=True)
    
#     print(conn.noop())

    # msg_uids = conn.search('4428')
    # print(msg_uids)

    # for msg_seq,data in conn.fetch(msg_uids,['RFC822']).items():
    #     email_msg = email.message_from_bytes(data[b"RFC822"],_class=email.message.EmailMessage)
    #     email_subject = email_msg.get("Subject")
    #     print(msg_seq,email_subject)



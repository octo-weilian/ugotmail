import email
from urllib import response
from mail.client import Mail
import keyring
import email

outlook_client = Mail("outlook.office365.com",993,
                            keyring.get_credential("HOTMAIL",None).username,
                            keyring.get_credential("HOTMAIL",None).password)

icloud_client = Mail("imap.mail.me.com",993,
                    keyring.get_credential("APPLE",None).username,
                    keyring.get_credential("APPLE",None).password)

with outlook_client.connection() as conn:
    # inbox = conn.select_folder("INBOX",readonly=True)
    
    print(conn.noop())
    


        
    
   
    


    

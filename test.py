import email
from urllib import response
from mail.client import Mail
import keyring
import email

test_client = Mail("outlook.office365.com",993,
                            keyring.get_credential("HOTMAIL",None).username,
                            keyring.get_credential("HOTMAIL",None).password)

with test_client.connection() as conn:
    inbox = conn.select_folder("INBOX",readonly=True)
    print(conn.search('4300'))
    


        
    
   
    


    

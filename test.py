import email
from re import L
from urllib import response
from mail.client import Mail
import keyring
import email

test_client = Mail("outlook.office365.com",993,
                            keyring.get_credential("HOTMAIL",None).username,
                            keyring.get_credential("HOTMAIL",None).password
                            )

with test_client.connection() as conn:

    inbox = conn.select_folder("INBOX",readonly=True)
    # message = conn.search('4500')
    uid, data = next(iter(conn.fetch([], ["ENVELOPE","RFC822"]).items()))
    email_message = email.message_from_bytes(data[b"RFC822"],_class=email.message.EmailMessage)
    email_subject = email_message.get('Subject')
    attachments = [part.get_filename() for part in email_message.iter_attachments()]
    
 
    print(email_subject)
        


            

        
        
   
    


    

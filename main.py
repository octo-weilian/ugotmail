import keyring
from mail.client import Mail
import schedule
import time

if __name__ == '__main__':
    #instantiate a background process
    outlook_inbox = Mail("outlook.office365.com",
                        keyring.get_credential("HOTMAIL",None).username,
                        keyring.get_credential("HOTMAIL",None).password)
    
    apple_inbox = Mail("imap.mail.me.com",
                        keyring.get_credential("APPLE",None).username,
                        keyring.get_credential("APPLE",None).password)
    
    outlook_inbox.sync(1)
    apple_inbox.sync(1)

    while True:
        schedule.run_pending()
        time.sleep(1)
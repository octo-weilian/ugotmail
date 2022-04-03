from mail.client import Watchdog
import keyring
from threading import Thread

if __name__ == '__main__':
    #instantiate a background process
    outlook_inbox = Watchdog(server="outlook.office365.com",
                                    port=993,
                                    user=keyring.get_credential("HOTMAIL",None).username,
                                    secret=keyring.get_credential("HOTMAIL",None).password,
                                    queue_size=20,
                                    parse_interval=15)
    
    icloud_inbox = Watchdog(server="imap.mail.me.com",
                                    port=993,
                                    user=keyring.get_credential("APPLE",None).username,
                                    secret=keyring.get_credential("APPLE",None).password,
                                    queue_size=20,
                                    parse_interval=15)
    
    Thread(target=outlook_inbox.monitor).start()
    Thread(target=icloud_inbox.monitor).start()
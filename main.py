from mail.client import Watchdog
import keyring
from threading import Thread

if __name__ == '__main__':
    #instantiate a background process
    watchdog_process_1 = Watchdog(server="outlook.office365.com",
                                    port=993,
                                    user=keyring.get_credential("HOTMAIL",None).username,
                                    secret=keyring.get_credential("HOTMAIL",None).password,
                                    queue_size=20,
                                    name='watchdog hotmail')
    
    watchdog_process_2 = Watchdog(server="imap.mail.me.com",
                                    port=993,
                                    user=keyring.get_credential("APPLE",None).username,
                                    secret=keyring.get_credential("APPLE",None).password,
                                    queue_size=20,
                                    name='watchdog apple')

    Thread(target=watchdog_process_1.monitor).start()
    Thread(target=watchdog_process_2.monitor).start()
from mail.client import Watchdog
import keyring

if __name__ == '__main__':
    #instantiate a background process
    watchdog_process = Watchdog(server="outlook.office365.com",
                                port=993,
                                user=keyring.get_credential("HOTMAIL",None).username,
                                secret=keyring.get_credential("HOTMAIL",None).password,
                                queue_size=20
                                )
    
    watchdog_process.monitor()

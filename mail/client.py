from . import logging
from contextlib import contextmanager
from imapclient import IMAPClient
import time
import email
import random
import string

#instantiate custom logger
LOGGER = logging.init_logger()

class Mail:

    #input parameters
    def __init__(self,server,port,user,secret):
        self.server = server
        self.port = port
        self.user = user
        self.secret = secret
    
    #connection handler
    @contextmanager
    def connection(self):
        try:
            self.client = IMAPClient(self.server,self.port)
            login = self.client.login(self.user,self.secret)
            if login:
                alias =  '*'*len(self.user.split('@')[0]) +'@'+ self.user.split('@')[-1]
                LOGGER.info(f"Connected to {self.server} with {alias}.")
                yield self.client
        except Exception as e:
            LOGGER.error(f"Disconnected with error: {e}")
            self.client.logout()
        finally:
            LOGGER.info('Disconnected')
            self.client.logout()

    #idle mode method
    def run_idle(self,task_queue=None,idle_timeout=30,idle_refresh=780):
        with self.connection() as conn:
            inbox = conn.select_folder("INBOX",readonly=True)
            conn.idle()
            start_time = int(time.monotonic())+idle_refresh
            LOGGER.info('Entered IDLE mode')
            while True:
                try:
                    idle_response = conn.idle_check(timeout=idle_timeout)
                    if len(idle_response)>0 and idle_response[0][1].decode()=="RECENT":
                        LOGGER.info(f"You got mail! IMAP response: {idle_response}")
                        recent_mails,total_mails = idle_response
                        if task_queue:
                            task_queue.put(total_mails[0])
                except Exception as e:
                    LOGGER.error("Exited IDLE mode with error: {e}")
                    conn.idle_done()
                    break
                finally:
                    run_time = int(time.monotonic())
                    if start_time-run_time<=0:
                        conn.idle_done()
                        conn.idle()
                        start_time = run_time+idle_refresh
                        LOGGER.info("IDLE refreshed!")

    #method to parse mail
    def parse_mail(self,mail_index):
        with self.connection() as conn:
            try:
                inbox = conn.select_folder("INBOX", readonly = True)
                message = conn.search(str(mail_index))
                for uid, message_data in conn.fetch(message, "RFC822").items():
                    email_message = email.message_from_bytes(message_data[b"RFC822"])
                    email_subject = email_message.get("Subject")
                    LOGGER.info(f"Mail nr. {mail_index} with subject: {email_subject}")
            except Exception as e:
                LOGGER.error(f"Failed to parse mail with index {mail_index}: {e}")
    
    #handle any task in queue
    def handle_tasks(self,task_queue):
        while True:
            self.parse_mail(task_queue.get())
            task_queue.task_done()

        







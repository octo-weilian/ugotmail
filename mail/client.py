from . import logging
from contextlib import contextmanager
from imapclient import IMAPClient
from queue import Queue
import time
import email

#instantiate custom logger
LOGGER = logging.init_logger()

class Mail:

    #input parameters
    def __init__(self,server:str,port:int,user:str,secret:str)->None:
        self.server = server
        self.port = port
        self.user = user
        self.secret = secret

    #connection handler
    @contextmanager
    def connection(self)->IMAPClient:
        try:
            self.client = IMAPClient(self.server,self.port)
            login = self.client.login(self.user,self.secret)
            if login:
                yield self.client
        except Exception as e:
            LOGGER.error(f"Unable to connect to {self.server}. Exited with error: {e}")
            self.client.logout()
        finally:
            self.client.logout()

    #idle mode method
    def run_idle(self,task_queue:Queue=None,idle_timeout:int=10,idle_refresh:int=900)->None:
        with self.connection() as conn:
            LOGGER.info(f"Listening to {self.server}...")
            inbox = conn.select_folder("INBOX",readonly=True)
            conn.idle()
            start_time = int(time.monotonic())+idle_refresh
            while True:
                try:
                    idle_response = conn.idle_check(timeout=idle_timeout)
                    if len(idle_response)>0 and idle_response[0][1].decode()=="RECENT":
                        recent_mails,total_mails = idle_response
                        if task_queue:
                            task_queue.put(total_mails[0])
                except Exception as e:
                    LOGGER.error(f"Disconnected with error: {e}")
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
    def parse_mail(self,mail_index:int)->None:
        with self.connection() as conn:
            try:
                inbox = conn.select_folder("INBOX", readonly = True)
                message = conn.search(str(mail_index))
                uid, message_data = next(iter(conn.fetch(message, "RFC822").items()))
                email_message = email.message_from_bytes(message_data[b"RFC822"])
                email_subject = email_message.get("Subject")
                LOGGER.info(f"Mail nr. {mail_index} with subject: {email_subject}")
            except Exception as e:
                LOGGER.error(f"Failed to parse mail with index {mail_index}: {e}")
    
    #handle any task in queue
    def handle_tasks(self,task_queue:Queue)->None:
        while True:
            self.parse_mail(task_queue.get())
            task_queue.task_done()

        







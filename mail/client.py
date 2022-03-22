from contextlib import contextmanager
from threading import Thread
from imapclient import IMAPClient
import queue
import time
import email
from . import logginghandler
import schedule

#instantiate custom logger
LOGGER = logginghandler.init_logger()

#mail client
class Mail:

    #input IMAP and authentication parameters
    def __init__(self,server:str,port:int,user:str,secret:str)->None:
        self.server = server
        self.port = port
        self.user = user
        self.secret = secret

    #connection handler
    @contextmanager
    def connection(self)->IMAPClient:
        try:
            self.client = IMAPClient(self.server,self.port,use_uid=True)
            if (login:=self.client.login(self.user,self.secret)):
                yield self.client
        except Exception as e:
            LOGGER.error(f"Unable to connect to {self.server}. Exited with error: {e}")
            self.client.logout()
        finally:
            self.client.logout()

    #method to enter idle mode
    def run_idle(self,task_queue:queue.Queue=None,idle_timeout:int=10,idle_refresh:int=900)->None:
        with self.connection() as conn:
            LOGGER.info(f"Listening to {self.server}...")
            inbox = conn.select_folder("INBOX",readonly=True)
            conn.idle()
            start_time = int(time.monotonic())+idle_refresh
            while True:
                try:
                    idle_response = conn.idle_check(timeout=idle_timeout)
                    idle_condition = len(idle_response)>0 and idle_response[0][1].decode()=="RECENT"
                    if idle_condition and task_queue:
                        msg_seq = idle_response[-1][0]
                        task_queue.put(msg_seq)
                except Exception as e:
                    LOGGER.error(f"Disconnected with error: {e}")
                    conn.idle_done()
                    break
                finally:
                    #refresh IDLE every --> idle_refresh
                    run_time = int(time.monotonic())
                    if start_time-run_time<=0:
                        conn.idle_done()
                        conn.idle()
                        start_time = run_time+idle_refresh
    
    #method to parse mail
    def parse_msg(self,msg_uid:int)->None:
        with self.connection() as conn:
            inbox = conn.select_folder("INBOX", readonly = True)
            try:
                data = next(iter(conn.fetch(msg_uid, "RFC822").items()))[-1]
                email_msg = email.message_from_bytes(data[b"RFC822"],_class=email.message.EmailMessage)
                email_subject = email_msg.get("Subject")
                email_attachments = self.get_attachments(email_msg)
                LOGGER.info(f"UID: {msg_uid} Subject: {email_subject} Attachments: {email_attachments}")
            except Exception as e:
                LOGGER.error(f"Failed to parse mail with UID {msg_uid}: {e}")
    
    def get_attachments(self,email_msg):
        return [part.get_filename() for part in email_msg.iter_attachments()]
        
    #method to get uid from message sequence
    def get_uid(self,msg_seq:int)->None:
        with self.connection() as conn:
            inbox = conn.select_folder("INBOX",readonly=True)
            return conn.search(str(msg_seq))
            
    #method to handle incoming MSN (message sequence number)
    def handle_seq(self,seq_queue:queue.Queue,uid_queue:queue.Queue)->None:
        while True:
            uid_queue.put(self.get_uid(seq_queue.get()))
            seq_queue.task_done()

    def handle_uid(self,uid_queue:queue.Queue):
        #run this every 30 minutes
        cached_uids = []
        while True:
            try:
                cached_uids.append(uid_queue.get(False))
            except queue.Empty:
                print(f'Decomposing {len(cached_uids)} msgs..')
                break
            else:
                uid_queue.task_done()

#monitoring
class Watchdog():
    def __init__(self,server,port,user,secret,queue_size=10):
        self.producer = Mail(server,port,user,secret)
        self.consumer = Mail(server,port,user,secret)
        self.decomposer = Mail(server,port,user,secret)
        self.seq_queue = queue.Queue(maxsize=queue_size)
        self.uid_queue = queue.Queue(maxsize=queue_size)
        
    def monitor(self):
        #spawn a background task which monitors new messages and put into the queue as task
        Thread(target=self.producer.run_idle,args=(self.seq_queue,),daemon=True).start()
        
        #spawn a consumer that fetch and processes any new task from the queue
        Thread(target=self.consumer.handle_seq,args=(self.seq_queue,self.uid_queue)).start()

        #decompose/ parse message uids on schedule
        schedule.every(30).minutes.do(self.decomposer.handle_uid,self.uid_queue)
        while True:
            schedule.run_pending()
            


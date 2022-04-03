from contextlib import contextmanager
from threading import Thread
from imapclient import IMAPClient
import queue
import time
import email
import logging
import schedule
from datetime import datetime
from . import parser
import re


#instantiate custom logger
LOGGER = logging.getLogger("logger")

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
    def run_idle(self,seq_queue:queue.Queue=None,idle_timeout:int=10,idle_reset:int=900)->None:
        with self.connection() as conn:
            LOGGER.info(f"Listening to {self.server}...")
            inbox = conn.select_folder("INBOX",readonly=True)
            conn.idle()
            start_time = int(time.monotonic())+idle_reset
            while True:
                try:
                    idle_response = conn.idle_check(timeout=idle_timeout)
                    if seq_queue and (msg_seq:=self.get_seq(idle_response)):
                        seq_queue.put(msg_seq)
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
                        start_time = run_time+idle_reset
    
    def get_seq(self,idle_response):
        match = re.search("\((\d+), b'EXISTS'",str(idle_response))
        if match:
            return match.group(1)

    #method to handle incoming message sequences to message UIDs
    def handle_seq(self,seq_queue:queue.Queue,uid_queue:queue.Queue,snooze:int=900)->None:
        with self.connection() as conn:
            inbox = conn.select_folder("INBOX",readonly=True)
            start_time = int(time.monotonic())+snooze
            while True:
                try:
                    msg_seq = seq_queue.get()
                    msg_uid = conn.search(str(msg_seq))[0]
                    uid_queue.put(msg_uid)
                    seq_queue.task_done()
                except Exception as e:
                    LOGGER.error(f"Disconnected with error: {e}")
                    break
                finally:
                    #reset connection every --> snooze
                    run_time = int(time.monotonic())
                    if start_time-run_time<=0:
                        conn.noop()
                        start_time = run_time+snooze

    #method to parse message (executed on scheduled call)
    def handle_uid(self,uid_queue:queue.Queue):
        cached_uids = []
        while True:
            try:
                cached_uids.append(uid_queue.get(False))
            except queue.Empty:
                if cached_uids:
                    cached_uids = list(set(cached_uids))
                    with self.connection() as conn:
                        inbox = conn.select_folder("INBOX",readonly=True)
                        parser.parse_msgs(conn,cached_uids)
                break
            else:
                uid_queue.task_done()

#monitoring
class Watchdog:
    
    #initialize mail sessions and in memory queues
    def __init__(self,server,port,user,secret,queue_size=10,parse_interval=30):
        self.producer = Mail(server,port,user,secret)
        self.consumer = Mail(server,port,user,secret)
        self.decomposer = Mail(server,port,user,secret)
        self.seq_queue = queue.Queue(maxsize=queue_size)
        self.uid_queue = queue.Queue(maxsize=queue_size)
        self.parse_interval = parse_interval
    
    #start monitoring mailbox
    def monitor(self):
        #spawn a background task which monitors new messages and put into queue 
        Thread(target=self.producer.run_idle,args=(self.seq_queue,),daemon=True).start()
        
        #spawn a consumer that fetch and processes any new task from the queue
        Thread(target=self.consumer.handle_seq,args=(self.seq_queue,self.uid_queue)).start()

        #schedule a decomposer that parses new messages
        if self.parse_interval > 0:
            schedule.every(self.parse_interval).minutes.do(self.decomposer.handle_uid,self.uid_queue)
            while True:
                schedule.run_pending()
                time.sleep(1)
            


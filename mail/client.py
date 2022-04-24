from contextlib import contextmanager
from imapclient import IMAPClient
import time
import email
import schedule
import json
import os
from .logginghandler import LOGGER
from .parser import parse_msgs
import configparser

CONFIG = configparser.ConfigParser()
CACHEFILE = "logs/cacheUID.ini"
CONFIG.read(CACHEFILE)

#mail client
class Mail:

    #input IMAP and authentication parameters
    def __init__(self,server,user,secret):
        self.server = server
        self.user = user
        self.secret = secret
        if not CONFIG.has_section(self.server):
            self.make_uid()

    #connection handler
    @contextmanager
    def connection(self)->IMAPClient:
        try:
            client = IMAPClient(self.server)
            if (login:=client.login(self.user,self.secret)):
                mailbox = client.select_folder(folder="INBOX",readonly=True)
                yield client
        except Exception as e:
            LOGGER.error(f"Unable to connect to {self.server}: {e}")
            pass
        finally:
            client.logout()

    def read_uid(self):
        storedUID,lastSync = CONFIG[self.server].values()
        return int(storedUID),int(lastSync)
    
    def make_uid(self,uid = None):
        if not uid:
            with self.connection() as conn:
                uid = conn.search("ALL")[-1]
        with open(CACHEFILE,"w") as f:
            CONFIG[self.server] = {"UID":uid,"lastsync":int(time.time())}
            CONFIG.write(f)
        
    def parse_uids(self):
        storedUID,lastSync = self.read_uid()
        with self.connection() as conn:
            if (server_uid:=conn.search("ALL")[-1])> storedUID:
                uids = conn.search(f"UID {storedUID}:*")[1:]
                parse_msgs(conn,uids)       #download message
                self.make_uid(server_uid)   #set new uid
                
    def sync(self,poll_freq=15):
        LOGGER.info(f"Listening to {self.server}")
        schedule.every(poll_freq).minutes.do(self.parse_uids)


            


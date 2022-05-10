from . import *
from . import parser
from threading import Thread
from contextlib import contextmanager
from imapclient import IMAPClient,SocketTimeout

#cache uid refresh rate 
CACHE_UID_REFRESH_HOURS = int(APP_CONFIG['client']['uid_refresh_rate']) 
REFRESH_MAX = CACHE_UID_REFRESH_HOURS * 3600

#client timeout (30s for connecting/ 600s for reading)
CONNECTION_TIMEOUT = int(APP_CONFIG['client']['connection_timeout'])
READING_TIMEOUT = int(APP_CONFIG['client']['reading_timeout'])
CLIENT_TIMEOUT = SocketTimeout(connect=CONNECTION_TIMEOUT, read=READING_TIMEOUT)

#additional search patterns
SEARCH_PATTERNS = []

#mail client
class Mail:

    #input IMAP and authentication parameters
    def __init__(self,server,port,ssl,folder,session_name):

        self.server = server 
        self.port = port
        self.ssl = ssl
        self.folder = folder
        self.session_name = session_name

        self.user = json.loads(os.getenv(session_name)).get("username")
        self.secret = json.loads(os.getenv(session_name)).get("secret")

        if not CACHE_CONFIG.has_section(session_name):
            self.make_uid()

    #connection handler
    @contextmanager
    def connection(self)->IMAPClient:
        try:
            client = IMAPClient(self.server,port=self.port,ssl=self.ssl,timeout=CLIENT_TIMEOUT)
            if (login:=client.login(self.user,self.secret)):
                mailbox = client.select_folder(folder=self.folder,readonly=True)
                yield client
        except Exception as e:
            LOGGER.error(f"Unable to connect to {self.server}: {e}")
        finally:
            client.logout()

    def test_connection(self):
        with self.connection() as conn:
            return True

    def read_uid(self):
        stored_uid,last_synced = CACHE_CONFIG[self.session_name].values()
        return int(stored_uid),int(last_synced)
    
    def make_uid(self,uid = None):
        if not uid:
            with self.connection() as conn:
                uid = conn.search("RECENT ALL")[-1]
        with open(CACHE_INI,"w") as f:
            CACHE_CONFIG[self.session_name] = {"uid":uid,"lastsynced":int(time.time())}
            CACHE_CONFIG.write(f)
        
    def parse_uids(self):
        stored_uid,last_synced = self.read_uid()
        try:
            with self.connection() as conn:
                if (server_uid:=conn.search("RECENT ALL")[-1])> stored_uid:
                    search_on = [f"UID {stored_uid}:*"] + SEARCH_PATTERNS
                    uids = conn.search(search_on)[1:]
                    parser.parse_msgs(conn,uids)       #parse messages
        except Exception as e:
            LOGGER.error(f"Unable to parse UIDs {stored_uid}/{server_uid}: {e}")
        finally:
            if (time.time()-last_synced) >= REFRESH_MAX:
                LOGGER.info(f"Cached UID renewed with: {server_uid}")
                self.make_uid(server_uid)  #refresh uid
        
    def schedule_poll(self,poll_freq=4):
        if poll_freq<=6:
            minute_marks = list(range(0,60,int((60/poll_freq))))
            for mark in minute_marks:
                schedule.every().hours.at(f":{str(mark).zfill(2)}").do(self.parse_uids)
            
            LOGGER.info(f"Listening to {self.session_name} every {int((60/poll_freq))} minutes.")
           
                
class Watchdog:
    def __init__(self):

        for i in range(len(APP_CONFIG.sections())):
            section = APP_CONFIG.sections()[i]
            config = dict(APP_CONFIG[section])
            if config.get("server"):
                mail_session = Mail(server=config.get('server'),
                                    port=int(config.get('port')),
                                    ssl= bool(config.get('ssl')),
                                    folder=config.get('folder'),
                                    session_name = section
                                    )

                if mail_session.test_connection():
                    Thread(target=mail_session.schedule_poll,args= (int(config.get('poll')), )).start()
                
    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)
                            
        
            

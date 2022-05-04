from . import *

#sync age
LAST_SYNCED_DAYS = 5 
LAST_SYNCED_MAX = LAST_SYNCED_DAYS * 3600

#mail client
class Mail:

    #input IMAP and authentication parameters
    def __init__(self,server,port,ssl,win_credential,folder,session_name):
        self.server = server 
        self.port = port
        self.ssl = ssl
        self.user = keyring.get_credential(win_credential,None).username
        self.secret = keyring.get_credential(win_credential,None).password
        self.folder = folder
        self.session_name = session_name

        if not CACHE_CONFIG.has_section(self.session_name):
            self.make_uid()

    #connection handler
    @contextmanager
    def connection(self)->IMAPClient:
        try:
            client = IMAPClient(self.server,port=self.port,ssl=self.ssl)
            if (login:=client.login(self.user,self.secret)):
                mailbox = client.select_folder(folder=self.folder,readonly=True)
                yield client
        except Exception as e:
            LOGGER.error(f"Unable to connect to {self.server}: {e}")
        finally:
            client.logout()

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
        if (time.time()-last_synced) < LAST_SYNCED_MAX:
            with self.connection() as conn:
                if (server_uid:=conn.search("RECENT ALL")[-1])> stored_uid:
                    uids = conn.search(f"UID {stored_uid}:*")[1:]
                    parser.parse_msgs(conn,uids)       #download message
                    self.make_uid(server_uid)   #set new uid
        else:
            LOGGER.error(f'Cached UID {self.session_name} is older than {LAST_SYNCED_DAYS} days')
    
    def schedule_poll(self,poll_freq=15):
        if poll_freq>10:
            LOGGER.info(f"Listening to {self.server} ({poll_freq} min. poll interval)")
            schedule.every(poll_freq).minutes.do(self.parse_uids)

class Watchdog:
    def __init__(self):
        for section in IMAP_CONFIG.sections():
            config = dict(IMAP_CONFIG[section])
            mail_session = Mail(server=config.get('server'),
                                port=int(config.get('port')),
                                ssl=config.get('ssl'),
                                win_credential=config.get('wincredential'),
                                folder=config.get('folder'),
                                session_name = section
                                )
            mail_session.schedule_poll(poll_freq=int(config.get('poll')))
        
    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)
                            
        
            

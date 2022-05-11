from mail import *
from mail.client import Mail
import mail
from email import utils
from mail.parser import ExtraParsers

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
        with mail_session.connection() as conn:
        
            uids = conn.search("RECENT ALL")[-5:]

            good_records = ExtraParsers(conn,uids).parse_posts()
            for l in good_records:
                print(l)


    

from mail import *
from mail.client import Mail
import mail
from email import utils

for i in range(len(IMAP_CONFIG.sections())):
    section = IMAP_CONFIG.sections()[i]
    config = dict(IMAP_CONFIG[section])
    mail_session = Mail(server=config.get('server'),
                                port=int(config.get('port')),
                                ssl=config.get('ssl'),
                                win_credential=config.get('wincredential'),
                                folder=config.get('folder'),
                                session_name = section
                                )

with mail_session.connection() as conn:
    uids = conn.search("RECENT ALL")[-20:]
    tzs = [[str(tz)] for tz in parser.parse_msgs(conn,uids)]
    
    
import psycopg2
from psycopg2.extras import execute_values    
from psycopg2.pool import SimpleConnectionPool
import keyring
from contextlib import contextmanager

pool = SimpleConnectionPool(minconn=1, maxconn=5,
                            user = keyring.get_credential('pgapp',None).username,
                            password = keyring.get_credential('pgapp',None).password,
                            host = 'localhost',
                            port = 5432,
                            database = 'inboek'
                            )

@contextmanager
def get_conn():
    try:
        connection = pool.getconn()
        yield connection
    except (Exception, psycopg2.Error) as e:
        print(f"Error while transaction: {e}")
    finally:
        pool.putconn(connection)

#insert queries
INSERT_DOSSIER = """INSERT INTO timestamp_demo (tstz) VALUES %s RETURNING ID;"""

def add_data(connection,values):
    with connection,connection.cursor() as cursor:
        execute_values(cursor,INSERT_DOSSIER,values)
        ids = cursor.fetchall()
        return ids

print(tzs[0])

# with get_conn() as conn:
#     add_data(conn,tzs)
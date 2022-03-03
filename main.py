from mail.client import Mail
import concurrent.futures
from queue import Queue
import keyring

def main():

    SHARED_QUEUE = Queue(maxsize=10)

    producer_client = Mail("outlook.office365.com",993,
                            keyring.get_credential("HOTMAIL",None).username,
                            keyring.get_credential("HOTMAIL",None).password
                            )
    consumer_client = Mail("outlook.office365.com",993,
                            keyring.get_credential("HOTMAIL",None).username,
                            keyring.get_credential("HOTMAIL",None).password
                            )
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        producer_worker = executor.submit(producer_client.run_idle,SHARED_QUEUE)
        consumer_worker = executor.submit(consumer_client.handle_tasks,SHARED_QUEUE)
        producer_worker.result()
        consumer_worker.result()

if __name__ == '__main__':
    main()

# import email
# from urllib import response
# from mail.client import Mail
# import keyring
# import email

# test_client = Mail("outlook.office365.com",993,
#                             keyring.get_credential("HOTMAIL",None).username,
#                             keyring.get_credential("HOTMAIL",None).password
#                             )

# with test_client.connection() as conn:

#     inbox = conn.select_folder("INBOX",readonly=True)
#     # message = conn.search('4500')
#     uid, data = next(iter(conn.fetch([], ["ENVELOPE","RFC822"]).items()))
#     email_message = email.message_from_bytes(data[b"RFC822"],_class=email.message.EmailMessage)
#     email_subject = email_message.get('Subject')
#     attachments = [part.get_filename() for part in email_message.iter_attachments()]
    
 
    # print(email_subject)

import queue
import time
import schedule
q = queue.Queue(maxsize=50)

for item in range(30):
    q.put(item)



def scheduler()
    schedule.every(5).seconds.do(timer)
    while True:
        n = schedule.idle_seconds()
        if n is None:
            timer()
        elif n>0:
            time.sleep(1)
        schedule.run_pending()

# def foo():
#     ids = []
#     while True:
#         try:
#             ids.append(q.get(False))
#         except queue.Empty:
#             break
#         else:
#             q.task_done()      
#     print(ids) 
    
# foo()

        
        
   
    


    

from dataclasses import dataclass
import email
from email import message
#import getpass
import imaplib
import os
import re
#import sys
from .exception_handler import ApplicationException


@dataclass
class EmailHandler:
    smtp_server = ''
    user_name = ''
    password = ''
    download_folder= ''

    def __init__(self, imap_server, user_name: str, password: str, download_folder) -> None:
        ApplicationException.when(not isinstance(imap_server, str), 'IMAP Server invalid')
        ApplicationException.when(not isinstance(user_name, str), 'User name invalid')
        ApplicationException.when(not isinstance(password, str), 'Password invalid')
        imap_server.strip()
        user_name.strip()
        password.strip()
        ApplicationException.when(imap_server == '', 'IMAP Server not specified')
        ApplicationException.when(user_name == '', 'User name not specified')
        ApplicationException.when(password == '', 'Password not specified')

        self.imap_name = imap_server
        self.user_name = user_name
        self.password = password
        self.download_folder = download_folder
        
    def get_email_infos(self, email_message: message.Message) -> tuple:
        subject = ''
        sender = ''
        rec_date = ''

        for el in email_message._headers:
            key = el[0].upper()
            if (key == 'FROM'):
                sender = el[1]
            elif (key == 'DATE'):
                rec_date = el[1]
            elif (key == 'SUBJECT'):
                subject = el[1]

        return subject, sender, rec_date

    def execute(self)->None:
        imap_session = imaplib.IMAP4_SSL(self.imap_name)
        imap_session.ssl = True
        result, account_details = imap_session.login(self.user_name, self.password)
        ApplicationException.when(result != 'OK', 'Not able to sign in!')

        imap_session.select('INBOX')
        result, messages = imap_session.uid('search', None, "ALL")
        ApplicationException.when(result != 'OK', 'Error searching Inbox.')
        
        messages_id = messages[0].split()

        for message_id in messages_id:
            result, email_data = imap_session.uid('fetch', message_id, '(RFC822)')
            raw_email = email_data[0][1]

            # converts byte literal to string removing b''
            raw_email_string = raw_email.decode('latin-1')
            email_message = email.message_from_string(raw_email_string)

            # downloading attachments
            for part in email_message.walk():
                # this part comes from the snipped I don't understand yet... 
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                att_file_name = part.get_filename()
                if (att_file_name):
                    att_file_name = re.sub("[:\\/\s]", "_", att_file_name)
                else:
                    att_file_name = 'sem_nome'
                    
                    

                if bool(att_file_name):
                    download_path = f"{self.download_folder}/{att_file_name}"
                    if not os.path.isfile(download_path) :
                        with open(download_path, 'wb') as file:
                            file.write(part.get_payload(decode=True))
            
            (subject, sender, rec_date) = self.get_email_infos(email_message)
                                    
            print(f'Downloaded "{att_file_name}" from "{sender}" titled "{subject}" on {rec_date}.')

        imap_session.logout()

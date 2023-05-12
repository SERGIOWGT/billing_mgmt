import base64
import datetime
import email
from dataclasses import dataclass

import imaplib
from mailbox import Message
import os
import quopri
import re
from typing import List
import uuid

from .Imail_handler import IEmailHandler
from src.infra.exception_handler import ApplicationException

@dataclass
class EmailHandler(IEmailHandler):
    imap_session: imaplib.IMAP4_SSL = None

    def logout(self)->None:
        self.imap_session.logout()

    def login(self, host: str, user_name: str, password: str, use_ssl: True) -> None:
        ApplicationException.when(not isinstance(host, str), 'Host invalid')
        ApplicationException.when(not isinstance(user_name, str), 'User name invalid')
        ApplicationException.when(not isinstance(password, str), 'Password invalid')
        host.strip()
        user_name.strip()
        password.strip()
        ApplicationException.when(host == '', 'Host not specified')
        ApplicationException.when(user_name == '', 'User name not specified')
        ApplicationException.when(password == '', 'Password not specified')

        self.imap_session = imaplib.IMAP4_SSL(host)
        self.imap_session.ssl = use_ssl

        (result, account_details) = self.imap_session.login(user_name, password)
        ApplicationException.when(result != 'OK', 'Not able to sign in!')

    def get_messages_id(self, folder: str)->List[int]:
        self.imap_session.select(folder)
        result, messages = self.imap_session.uid('search', None, "ALL")
        ApplicationException.when(result != 'OK', 'Error searching Inbox.')

        return messages[0].split()

    def get_email_infos(self, message_uid: int) -> tuple:
        (result, email_data) = self.imap_session.uid('fetch', message_uid, '(RFC822)')
        ApplicationException.when(result != 'OK', f'Error fetching message {message_uid}')

        if (len(email_data) > 0) and email_data[0] is None:
            return '', ''

        raw_email = email_data[0][1]
        raw_email_string = raw_email.decode('latin-1')
        email_message = email.message_from_string(raw_email_string)

        subject = ''
        sender = ''
        rec_date = ''
        has_attachment = False

        for el in email_message._headers:
            key = el[0].upper()
            if (key == 'FROM'):
                sender = el[1]
            elif (key == 'DATE'):
                rec_date = el[1]
            elif (key == 'SUBJECT'):
                subject = el[1]

        for part in email_message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            has_attachment = True

        return subject, sender, rec_date, has_attachment

    def fetch_email(self, message_uid: int)-> Message:
        (result, email_data) = self.imap_session.uid('fetch', message_uid, '(RFC822)')
        ApplicationException.when(result != 'OK', f'Error fetching message {message_uid}')
        raw_email = email_data[0][1]
        raw_email_string = raw_email.decode('latin-1')
        return email.message_from_string(raw_email_string)

    def encoded_file_name_2_text(self, encoded_words):
        encoded_word_regex = r'=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}='
        if not re.match(encoded_word_regex, encoded_words):
            return encoded_words

        charset, encoding, encoded_text = re.match(encoded_word_regex, encoded_words).groups()
        if encoding == 'B':
            byte_string = base64.b64decode(encoded_text)
        elif encoding == 'Q':
            byte_string = quopri.decodestring(encoded_text)

        return byte_string.decode(charset)

    def get_save_attachments(self, message_uid: int, download_folder: str):
        list_file = []
        email_message = self.fetch_email(message_uid)
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S").replace('-', '_')

        for part in email_message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            guid = uuid.uuid4()
            att_file_name = f"{timestamp}_{guid}.pdf"
            #att_file_name = part.get_filename()
            #if (att_file_name):
            #    att_file_name = self.encoded_file_name_2_text(att_file_name)
            #    att_file_name = re.sub("[:\\/\s]", "_", att_file_name)
            #else:
            #    att_file_name = 'unkown_file_name'

            if bool(att_file_name):
                download_path = f"{download_folder}/{att_file_name}"
                if not os.path.isfile(download_path) :
                    with open(download_path, 'wb') as file:
                        file.write(part.get_payload(decode=True))

                list_file.append(att_file_name)

        return list_file

    def move(self, message_uid: int, destination_folder: str) -> None:
        (result, _) = self.imap_session.uid('move', message_uid, destination_folder)
        ApplicationException.when(result != 'OK', f'Error moving message {message_uid}')

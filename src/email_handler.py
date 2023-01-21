from dataclasses import dataclass
#import email
#import getpass
import imaplib
#import os
#import sys
from .exception_handler import ApplicationException


@dataclass
class EmailHandler:
    user_name = ''
    password = ''

    def __init__(self, user_name: str, password: str) -> None:
        ApplicationException.when(not isinstance(user_name, str), 'User name invalid')
        ApplicationException.when(not isinstance(password, str), 'Password invalid')
        user_name.strip()
        password.strip()
        ApplicationException.when(user_name == '', 'User name not specified')
        ApplicationException.when(password == '', 'Password not specified')

        self.user_name = user_name
        self.password = password

    def execute(self)->None:
        imapSession = imaplib.IMAP4_SSL('imap.gmail.com')
        imapSession.ssl = True
        typ, accountDetails = imapSession.login(self.user_name, self.password)

        ApplicationException.when(typ != 'OK', 'Not able to sign in!')

        imapSession.select('[Gmail]/All Mail')
        typ, data = imapSession.search(None, 'ALL')
        ApplicationException.when(typ != 'OK', 'Error searching Inbox.')

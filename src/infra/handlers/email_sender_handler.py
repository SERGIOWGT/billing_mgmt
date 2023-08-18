#
# CLASSE ESPECÍFICA PARA ENVIAR EMAIL DE UMA CONTA GMAIL ESPECÍFICA PARA QUALQUER CONTA DE EMAIL
#
from dataclasses import dataclass
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.infra.handlers.exception_handler import ApplicationException

@dataclass
class EmailSenderHandler():
    _host: str = ''
    _user_name: str = ''
    _password: str = ''

    def __init__(self, host: str, user_name: str, password: str):
        ApplicationException.when(not isinstance(host, str), 'Host invalid')
        ApplicationException.when(not isinstance(user_name, str), 'User name invalid')
        ApplicationException.when(not isinstance(password, str), 'Password invalid')
        host.strip()
        user_name.strip()
        password.strip()

        self._host = host
        self._user_name = user_name
        self._password = password

    def send(self, _from: str, _to: str, subject: str, body: str):
        ApplicationException.when(self._host == '', 'Host not specified')
        ApplicationException.when(self._user_name == '', 'User name not specified')
        ApplicationException.when(self._password == '', 'Password not specified')

        msg = MIMEMultipart()
        msg['From'] = _from
        msg['To'] = _to
        msg['Subject'] = subject
        msg.attach(MIMEText(body))
        
        mailserver = smtplib.SMTP(self._host, 587)
        # identify ourselves to smtp gmail client
        mailserver.ehlo()
        # secure our email with tls encryption
        mailserver.starttls()
        # re-identify ourselves as an encrypted connection
        mailserver.ehlo()
        mailserver.login(self._user_name, self._password)
        mailserver.sendmail(_from, _to, msg.as_string())

        mailserver.quit()

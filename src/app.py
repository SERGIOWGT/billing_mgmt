from dataclasses import dataclass
from .email_handler import EmailHandler

@dataclass
class App:
    @staticmethod
    def execute(smtp_server: str, user_name: str, password: str, download_folder: str)->None:
        email = EmailHandler(download_folder)
        
        email.login(smtp_server, user_name, password, use_ssl=True)
        messages_id = email.get_messages_id('INBOX')
        
        for message_uid in messages_id:
            files = email.get_files()
                
            if (files):
                print('salva')
        

        #email.execute()

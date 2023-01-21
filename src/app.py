from dataclasses import dataclass
from .email_handler import EmailHandler


@dataclass
class App:
    @staticmethod
    def execute(smtp_server: str, user_name: str, password: str, download_folder: str)->None:
        email = EmailHandler(smtp_server, user_name, password, download_folder) 

        email.execute()

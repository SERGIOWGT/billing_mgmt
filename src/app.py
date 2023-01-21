from dataclasses import dataclass
from .email_handler import EmailHandler


@dataclass
class App:
    @staticmethod
    def execute(user_name: str, password: str)->None:
        email = EmailHandler(user_name, password)

        email.execute()
        
    
   
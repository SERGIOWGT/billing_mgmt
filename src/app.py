from dataclasses import dataclass
from src.email_handler import EmailHandler

@dataclass
class App:
    @staticmethod
    def execute(smtp_server: str, user_name: str, password: str, download_folder: str, email_destination_folder: str)->int:
        num_emails = 0
        email = EmailHandler()

        email.login(smtp_server, user_name, password, use_ssl=True)
        messages_id = email.get_messages_id('INBOX')

        for message_uid in messages_id:
            (subject, sender, rec_date, has_attachments) = email.get_email_infos(message_uid)

            if (has_attachments):
                file_list = email.get_save_attachments(message_uid, download_folder)

                num_emails += 1
                email.move(message_uid, email_destination_folder)
                
                for file_name in file_list:
                    print(f'Downloaded "{file_name}" from "{sender}" titled "{subject}" on {rec_date}.')

        email.logout()
        return num_emails

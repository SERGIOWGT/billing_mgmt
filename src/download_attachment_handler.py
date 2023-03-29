import os
from dataclasses import dataclass
from src.infra.exception_handler import ApplicationException
from src.email_handler import EmailHandler

@dataclass
class DownloadAttachmentHandler:
    def __init__(self, path_to_save, input_email_folder, output_email_folder, log):
        ApplicationException.when(not os.path.exists(path_to_save), f'Path does not exist. [{path_to_save}]', log)
        self.path_to_save = path_to_save
        self.input_email_folder = input_email_folder
        self.output_email_folder = output_email_folder
        self.log = log

    def execute(self, smtp_server: str, user_name: str, password: str) -> int:
        num_emails = 0
        email = EmailHandler()

        email.login(smtp_server, user_name, password, use_ssl=True)
        messages_id = email.get_messages_id(self.input_email_folder)

        for message_uid in messages_id:
            (subject, sender, rec_date, has_attachments) = email.get_email_infos(message_uid)

            if (has_attachments):
                file_list = email.get_save_attachments(message_uid, self.path_to_save)

                num_emails += 1
                email.move(message_uid, self.output_email_folder)

                for file_name in file_list:
                    self.log.info(f'Downloaded "{file_name}" from "{sender}" titled "{subject}" on {rec_date}.')

        email.logout()
        return num_emails
    
import os
from dataclasses import dataclass
from src.infra.exception_handler import ApplicationException
from src.email_handler import EmailHandler

@dataclass
class DownloadAttachmentHandler:
    def __init__(self, log, config):
        self.config = config

        self.smtp_server = self.config.get('email.imap_server')
        self.user = self.config.get('email.user')
        self.password = self.config.get('email.password')
        self.input_email_folder = self.config.get('email.input_folder')
        self.output_email_folder = self.config.get('email.output_folder')

        self.path_to_save = self.config.get('directories.downloads')
        ApplicationException.when(not os.path.exists(self.path_to_save), f'Path does not exist. [{self.path_to_save}]', log)
        self.log = log

    def execute(self) -> int:
        num_emails = 0
        email = EmailHandler()

        email.login(self.smtp_server, self.user, self.password, use_ssl=True)
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
    
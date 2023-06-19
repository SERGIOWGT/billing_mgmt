from dataclasses import dataclass
from src.infra.email_handler.Imail_handler import IEmailHandler
from email.utils import parsedate_to_datetime

@dataclass
class AttachmentDownloader:
    @staticmethod
    def execute(path_to_save: str, input_email_folder: str, output_email_folder: str, log, email: IEmailHandler ) -> int:
        num_emails = 0
        num_files = 0
        messages_id = email.get_messages_id(input_email_folder)

        for message_uid in messages_id:
            (subject, sender, rec_date, has_attachments) = email.get_email_infos(message_uid)
            if (has_attachments):
                file_list = email.get_save_attachments(message_uid, path_to_save, parsedate_to_datetime(rec_date))

                num_emails += 1
                email.move(message_uid, output_email_folder)

                for file_name in file_list:
                    num_files += 1
                    log.info(f'Downloaded "{file_name}" from "{sender}" titled "{subject}" on {rec_date}.', instant_msg=True)

        return num_emails, num_files
    
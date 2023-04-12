from dataclasses import dataclass
from src.infra.email_handler.Imail_handler import IEmailHandler

@dataclass
class AttachmentDownloader:
    @staticmethod
    def execute(path_to_save, input_email_folder, output_email_folder, log, email: IEmailHandler, ) -> int:
        num_emails = 0
        messages_id = email.get_messages_id(input_email_folder)

        for message_uid in messages_id:
            (subject, sender, rec_date, has_attachments) = email.get_email_infos(message_uid)

            if (has_attachments):
                file_list = email.get_save_attachments(message_uid, path_to_save)

                num_emails += 1
                email.move(message_uid, output_email_folder)

                for file_name in file_list:
                    log.info(f'Downloaded "{file_name}" from "{sender}" titled "{subject}" on {rec_date}.')

        
        return num_emails
    
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
import os
from src.infra.email_handler.Imail_handler import IEmailHandler
from src.infra.email_handler.email_handler import EmailHandler
from src.infra.exception_handler import ApplicationException

@dataclass
class EmailApp:
    _smtp_server = ''
    _user = ''
    _password = ''
    _input_email_folder = ''
    _output_email_folder = ''
    _email_handler = None

    def _get_email_handler(self, log) -> IEmailHandler:
        log.info('Connecting Email...', instant_msg=True)
        email = EmailHandler()

        try:
            self._user = 'robotqd23@gmail.com'
            self._password = 'hgtyrvabzwumkiwu'
            email.login(self._smtp_server, self._user, self._password, use_ssl=True)
        except Exception as error:
            msg = str(error)
            log.critical(msg)
            raise ApplicationException('Error connecting email') from error

        return email

    def _download_files(self, email: IEmailHandler, log, temp_dir) -> int:
        num_emails = 0
        messages_id = email.get_messages_id(self._input_email_folder)

        all_files = []
        for message_uid in messages_id:
            (subject, sender, rec_date, has_attachments) = email.get_email_infos(message_uid)
            if (has_attachments):
                file_list = email.get_save_attachments(message_uid, temp_dir, parsedate_to_datetime(rec_date))

                num_emails += 1
                # email.move(message_uid, output_email_folder)

                for file_name in file_list:
                    log.info(f'Downloaded "{file_name}" from "{sender}" titled "{subject}" on {rec_date}.', instant_msg=True)

                all_files.extend(file_list)
                break

        return num_emails, all_files

    def execute(self, drive, log, smtp_server, user, password, input_email_folder, output_email_folder, temp_dir: str, work_folder_id: str):
        self._smtp_server = smtp_server
        self._user = user
        self._password = password
        self._input_email_folder = input_email_folder
        self._output_email_folder = output_email_folder

        log.info('Downloading PDF files from emails', instant_msg=True)
        email = self._get_email_handler(log)
        _, all_files = self._download_files(email, log, temp_dir)
        for file_name in all_files:
            complete_filename = os.path.join(temp_dir, file_name)
            log.info(f'Uploading email file {file_name}', instant_msg=True)
            drive.upload_file(local_file_name=complete_filename, file_name=file_name, parents=[work_folder_id])
            log.info(f'Removing file {file_name}', instant_msg=True)
            os.remove(complete_filename)
        email.logout()

        num_files = len(all_files)
        if num_files == 0:
            log.info('No files downloaded', instant_msg=True, warn=True)
        elif num_files == 1:
            log.info('1 file downloaded', instant_msg=True, warn=True)
        else:
            log.info(f'{num_files} files downloaded', instant_msg=True, warn=True)

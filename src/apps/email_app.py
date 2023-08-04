from dataclasses import dataclass
from email.utils import parsedate_to_datetime
import os
from src.infra.email_handler.email_reader_handler import EmailReaderHandler
from src.infra.exception_handler import ApplicationException

@dataclass
class EmailApp:
    _imap_server = ''
    _user = ''
    _password = ''
    _input_email_folder = ''
    _output_email_folder = ''
    _email_handler = None

    def _get_email_handler(self, log) -> EmailReaderHandler:
        log.save_message('Connecting Email...')
        email = EmailReaderHandler()

        try:
            email.login(self._imap_server, self._user, self._password, use_ssl=True)
            log.save_message('Email conected')
        except Exception as error:
            msg = str(error)
            log.save_message(msg, error=True)
            raise ApplicationException('Error connecting email') from error

        return email

    def execute(self, drive, log, imap_server, user, password, input_email_folder, output_email_folder, temp_dir: str, work_folder_id: str):
        self._imap_server = imap_server
        self._user = user
        self._password = password
        self._input_email_folder = input_email_folder
        self._output_email_folder = output_email_folder

        email = self._get_email_handler(log)
        messages_id = email.get_messages_id(self._input_email_folder)
        num_files = 0
        total_emails = len(messages_id)
        count_emails = 0
        num_emails = 0
        for message_uid in messages_id:
            (subject, sender, rec_date, has_attachments) = email.get_email_infos(message_uid)
            count_emails += 1
            log.save_message(f'Reading email ({count_emails}/{total_emails})')
            if has_attachments is False:
                email.move(message_uid, 'SEM_ATT')
                continue
     
            file_list = email.get_save_attachments(message_uid, temp_dir, parsedate_to_datetime(rec_date))
            num_emails += 1
            for file_name in file_list:
                num_files += 1
                log.save_message(f'Downloaded "{file_name}" from "{sender}" titled "{subject}" on {rec_date}.')
                complete_filename = os.path.join(temp_dir, file_name)
                log.save_message(f'Uploading email file {file_name}')
                drive.upload_file(local_file_name=complete_filename, file_name=file_name, parents=[work_folder_id])
                log.save_message(f'Removing file {file_name}')
                os.remove(complete_filename)
        
            email.move(message_uid, self._output_email_folder)

        email.logout()

        if num_files == 0:
            log.save_message('No files downloaded from gmail', execution=True)
        elif num_files == 1:
            log.save_message('1 file downloaded from gmail', execution=True)
        else:
            log.save_message(f'{num_files} files downloaded from gmail', execution=True)        
    
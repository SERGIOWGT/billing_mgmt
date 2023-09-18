from dataclasses import dataclass

from src.infra.handlers.exception_handler import ApplicationException
@dataclass
class EmailAppDto:
    def _handle_str_value(self, value: str, value_name: str) -> str:
        value = value or ''
        ApplicationException.when(value == '', f"'{value_name}' does not exist or empty.")
        return value

    def __init__(self, imap_server, user, password, input_email_folder, output_email_folder, temp_dir: str, work_folder_id: str):
        self.imap_server = self._handle_str_value(imap_server, 'imap_server')
        self.user = self._handle_str_value(user, 'user')
        self.password = self._handle_str_value(password, 'password')
        self.input_email_folder = self._handle_str_value(input_email_folder, 'input_email_folder')
        self.output_email_folder = self._handle_str_value(output_email_folder, 'output_email_folder')
        self.temp_dir = self._handle_str_value(temp_dir, 'temp_dir')
        self.work_folder_id = self._handle_str_value(work_folder_id, 'work_folder_id')

from dataclasses import dataclass
import os

from .contas_consumo_handler import ContaConsumoHandler
from .download_attachment_handler import DownloadAttachmentHandler
from src.infra.exception_handler import ApplicationException


@dataclass
class App:
    smtp_server = ''
    email_user = ''
    email_password = ''
    downloads_folder = ''
    export_folder = ''
    input_email_folder = ''
    output_email_folder = ''

    def __init__(self, config, log):
        self.downloads_folder = config.get('diretorios.downloads')
        ApplicationException.when(not os.path.exists(self.downloads_folder), f'Path does not exist. [{self.downloads_folder}]', log)

        self.export_folder = config.get('diretorios.export')
        ApplicationException.when(not os.path.exists(self.export_folder), f'Path does not exist. [{self.export_folder}]', log)
        self.log = log
        self.smtp_server = config.get('email.imap_server')
        self.email_user = config.get('email.user')
        self.email_password = config.get('email.password')
        self.input_email_folder = config.get('email.input_folder')
        self.output_email_folder = config.get('email.output_folder')

    def execute(self):
        downloader = DownloadAttachmentHandler(path_to_save=self.downloads_folder, input_email_folder=self.input_email_folder, output_email_folder=self.output_email_folder, log=self.log)
        try:
            downloader.execute(smtp_server=self.smtp_server, user_name=self.email_user, password=self.email_password)
        except Exception:
            raise

        handler = ContaConsumoHandler(self.downloads_folder, self.export_folder, self.log)
        try:
            handler.execute()
        except Exception:
            raise



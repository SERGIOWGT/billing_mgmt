from dataclasses import dataclass
import os

from .contas_consumo_handler import ContaConsumoHandler
from .download_attachment_handler import DownloadAttachmentHandler
from src.infra.exception_handler import ApplicationException


@dataclass
class App:
    def __init__(self, base_folder: str, log):
        ApplicationException.when(not os.path.exists(base_folder), f'Path does not exist. [{base_folder}]', log)
        self.log = log
        self.base_folder = base_folder
        self.save_folder = os.path.join(base_folder, "downloads")
        
        
    def execute(self, smtp_server: str, user_name: str, password: str):
        downloader = DownloadAttachmentHandler(path_to_save=self.save_folder, inbox_folder="INBOX", save_folder="PROCESSADOS", log=self.log)
        try:
            downloader.execute(smtp_server=smtp_server, user_name=user_name, password=password)
        except Exception:
            raise

        handler = ContaConsumoHandler(self.save_folder, self.log)
        try:
            handler.execute()
        except Exception:
            raise



from dataclasses import dataclass
import os

from .contas_consumo_handler import ContaConsumoHandler
from .download_attachment_handler import DownloadAttachmentHandler
from src.infra.exception_handler import ApplicationException


@dataclass
class App:

    def __init__(self, config, log, drive):
        self.downloads_folder = config.get('directories.downloads')
        ApplicationException.when(not os.path.exists(self.downloads_folder), f'Path does not exist. [{self.downloads_folder}]', log)

        self.export_folder = config.get('directories.exports')
        ApplicationException.when(not os.path.exists(self.export_folder), f'Path does not exist. [{self.export_folder}]', log)
        self.log = log
        self.drive = drive
        self.config = config

    def execute(self):
        downloader = DownloadAttachmentHandler(log=self.log, config=self.config)
        try:
            downloader.execute()
        except Exception:
            raise

        handler = ContaConsumoHandler(self.log, self.drive, self.config)
        try:
            handler.execute()
        except Exception:
            raise



from dataclasses import dataclass
import time
from typing import Any, List
from src.domain.entities.conta_consumo_base import ContaConsumoBase
from src.infra.google_drive_handler.Igoogle_drive_handler import IGoogleDriveHandler

@dataclass
class ResultsUploader:
    _log: Any
    _drive: IGoogleDriveHandler

    def __init__(self, log, drive: IGoogleDriveHandler):
        self._log = log
        self._drive = drive

    def execute(self, folder_base_id: str, ok_list: List[ContaConsumoBase])->None:
        for conta_ok in ok_list:
            new_parent_id = self._drive.find_file(conta_ok.diretorio_google, folder_base_id)
            if (new_parent_id is None):
                new_folder = self._drive.create_folder(conta_ok.diretorio_google, folder_base_id)
                self._log.info(f'Creating google drive directory {conta_ok.diretorio_google}')
                time.sleep(3)
                while (True):
                    new_parent_id = self._drive.find_file(conta_ok.diretorio_google, folder_base_id)
                    if (new_parent_id):
                        break
                    time.sleep(3)
                self._log.info('Created')
                new_folder = new_parent_id

            parents: List[str] = [new_parent_id]
            self._log.info(f'Uploading file {conta_ok.nome_arquivo_google}')
            self._drive.upload_file(conta_ok.file_name, conta_ok.nome_arquivo_google, parents)

        return

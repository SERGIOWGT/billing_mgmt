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

    def _create_folder(self, name, parent_id) -> str:
        folder_id = self._drive.find_file(name, parent_id)
        if folder_id:
            return folder_id

        new_folder = self._drive.create_folder(name, parent_id)
        time.sleep(3)
        while (True):
            new_parent_id = self._drive.find_file(name, parent_id)
            if (new_parent_id):
                break
            time.sleep(3)

        return new_folder

    def _create_file(self, original_file_name: str, google_file_name: str, parent_id: str) -> Any:
        file_id = self._drive.find_file(google_file_name, parent_id)
        if (file_id):
            file = self._drive.update_file(file_id, original_file_name)
        else:
            file = self._drive.upload_file(original_file_name, google_file_name, [parent_id])

        return file

    def execute(self, folder_base_id: str, ok_list: List[ContaConsumoBase])->None:
        for conta_ok in ok_list:
            self._log.info(f'Creating folder {conta_ok.diretorio_google}')
            folder_id = self._create_folder(conta_ok.diretorio_google, folder_base_id)

            self._log.info(f'Uploading file {conta_ok.nome_arquivo_google}')
            file = self._create_file(original_file_name=conta_ok.file_name, google_file_name=conta_ok.nome_arquivo_google, parent_id= folder_id)
            conta_ok.link_google = f'https://drive.google.com/file/d/{file["id"]}/view?usp=share_link'
        return

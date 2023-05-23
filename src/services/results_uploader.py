import os
import time
from dataclasses import dataclass

from typing import Any, List
from src.domain.enums.document_type_enum import DocumentTypeEnum

from src.domain.entities.response_error import UtilityBillIgnoredResponse, UtilityBillDuplicatedResponse, UtilityBillOkResponse, UtilityBillBaseResponse
from src.domain.entities.base.base_utility_bill import UtilityBillBase
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

        return new_parent_id

    def _create_file(self, original_file_name: str, google_file_name: str, parent_id: str) -> Any:
        try:
            file_id = self._drive.find_file(google_file_name, parent_id)
        except:
            file_id = file_id
        if (file_id):
            file = self._drive.update_file(file_id, original_file_name)
        else:
            file = self._drive.upload_file(original_file_name, google_file_name, [parent_id])

        return file

    def _create_excel_file(self, original_file_name: str, google_file_name: str, parent_id: str) -> Any:
        return self._drive.upload_file(original_file_name, google_file_name, [parent_id], 'application/vnd.ms-excel')

    def upload_ok_list(self, folder_base_id: str, folder_contabil_id: str, ok_list: List[UtilityBillOkResponse]) -> None:
        for resp in ok_list:
            self._log.info(f'Creating folder {resp.utility_bill.diretorio_google}', instant_msg=True)
            folder_id = self._create_folder(resp.utility_bill.diretorio_google, folder_base_id)

            if resp.utility_bill.tipo_documento == DocumentTypeEnum.CONTA_CONSUMO or \
                resp.utility_bill.tipo_documento == DocumentTypeEnum.CONTA_CONSUMO_RATEIO:
                data_base = resp.utility_bill.dt_vencimento
            else:
                data_base = resp.utility_bill.dt_emissao

            dir_name = data_base.strftime('%Y.%m')
            date_folder_id = self._create_folder(dir_name, folder_id)
            self._log.info(f'Uploading file {resp.utility_bill.nome_arquivo_google}', instant_msg=True)
            file = self._create_file(original_file_name=resp.complete_file_name, google_file_name=resp.utility_bill.nome_arquivo_google, parent_id=date_folder_id)
            resp.google_file_id = file["id"]
            if resp.utility_bill.is_qualquer_destino:
                self._log.info(f'Uploading file {resp.utility_bill.nome_arquivo_google} on accounting folder', instant_msg=True)

                folder_id = self._create_folder(dir_name, folder_contabil_id)
                file = self._create_file(original_file_name=resp.complete_file_name, google_file_name=resp.utility_bill.nome_arquivo_google, parent_id=folder_id)

        return

    def _upload_duplicate_list(self, folder_others_base_id: str, dupl_list: List[UtilityBillDuplicatedResponse]) -> None:
        self._log.info('Uploading error files - duplicates', instant_msg=True)
        for resp in dupl_list:
            self._log.info(f'Uploading file {resp.file_name}', instant_msg=True)
            file = self._create_file(original_file_name=resp.complete_file_name, google_file_name=resp.file_name, parent_id=folder_others_base_id)
            resp.google_file_id = file["id"]
        return

    def _upload_error_list(self, folder_others_base_id: str, error_list: List[UtilityBillBaseResponse]) -> None:
        self._log.info('Uploading error files', instant_msg=True)
        for resp in error_list:
            self._log.info(f'Uploading file {resp.file_name}', instant_msg=True)
            file = self._create_file(original_file_name=resp.complete_file_name, google_file_name=resp.file_name, parent_id=folder_others_base_id)
            resp.google_file_id = file["id"]
        return

    def _upload_ignored_list(self, folder_others_base_id: str, list: List[UtilityBillIgnoredResponse]) -> None:
        self._log.info('Uploading Ignored files', instant_msg=True)
        for conta in list:
            self._log.info(f'Uploading file {conta.file_name}', instant_msg=True)
            file = self._create_file(original_file_name=conta.complete_file_name, google_file_name=conta.file_name, parent_id=folder_others_base_id)
            conta.google_file_id = file["id"]

    def upload_other_list(self, folder_others_base_id: str, not_found_list: List[UtilityBillBase], error_list: List[UtilityBillBase], \
                            duplicated_list: List[UtilityBillDuplicatedResponse], ignored_list: List[UtilityBillIgnoredResponse]) -> None:
        self._upload_error_list(folder_others_base_id, not_found_list)
        self._upload_error_list(folder_others_base_id, error_list)
        self._upload_duplicate_list(folder_others_base_id, duplicated_list)
        self._upload_ignored_list(folder_others_base_id, ignored_list)

    def upload_results(self, folder_results_id: str, export_filename: str) -> None:
        file_name = os.path.basename(export_filename)
        exports_folder_id = self._create_folder('exports', folder_results_id)
        _ = self._create_excel_file(original_file_name=export_filename, google_file_name=file_name, parent_id=exports_folder_id)

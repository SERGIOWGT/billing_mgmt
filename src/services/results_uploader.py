import os
import time
import datetime
from dataclasses import dataclass

from typing import Any, List
from src.domain.enums.document_type_enum import DocumentTypeEnum
from src.domain.entities.response_error import UtilityBillIgnoredResponse, UtilityBillOkResponse, UtilityBillBaseResponse
from src.infra.handlers.google_drive_handler import GoogleDriveHandler


@dataclass
class ResultsUploader:
    _log: Any
    _drive: GoogleDriveHandler

    def __init__(self, log, drive: GoogleDriveHandler):
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

    def _copy_file(self, file_id, folder_id, file_name):
        file_id_searched = ''
        try:
            file_id_searched = self._drive.find_file(file_name, folder_id)
        except:
            ...

        if (file_id_searched):
            self._drive.delete_file(file_id=file_id_searched)

        return self._drive.copy_file(file_id, folder_id, file_name)

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

    def _save_previous_file(self, google_file_name: str, new_file_name, parent_id: str) -> None:
        try:
            file_id = self._drive.find_file(google_file_name, parent_id)
        except:
            file_id = file_id
            
        if (file_id):
            self._drive.rename_file(file_id, new_filename=new_file_name)

    def _create_excel_file(self, original_file_name: str, google_file_name: str, parent_id: str, overwrite=True) -> Any:
        if not overwrite:
            return self._drive.upload_file(original_file_name, google_file_name, [parent_id], 'application/vnd.ms-excel')
        
        try:
            file_id = self._drive.find_file(google_file_name, parent_id)
        except:
            file_id = file_id
        if (file_id):
            file = self._drive.update_file(file_id, original_file_name)
        else:
            file = self._drive.upload_file(original_file_name, google_file_name, [parent_id], 'application/vnd.ms-excel')

        return file
        #return self._drive.upload_file(original_file_name, google_file_name, [parent_id], 'application/vnd.ms-excel')

    def _upload_error_list(self, msg: str, folder_others_base_id: str, error_list: List[UtilityBillBaseResponse]) -> None:
        if len(error_list) == 0:
            return

        self._log.save_message(msg, execution=True)
        total = len(error_list)
        count = 0
        for resp in error_list:
            count = count + 1
            self._log.save_message(f'Uploading file {resp.file_name} ({count}/{total})')
            file = self._copy_file(file_id=resp.email_file_id, folder_id=folder_others_base_id, file_name=resp.file_name)
            resp.google_file_id = file["id"]
        return

    def _upload_ignored_list(self, folder_others_base_id: str, list: List[UtilityBillIgnoredResponse]) -> None:
        if len(list) == 0:
            return

        self._log.save_message('Copying Ignored files', execution=True)
        total = len(list)
        count = 0
        for conta in list:
            count = count + 1
            self._log.save_message(f'Copying file {conta.file_name} ({count}/{total})')
            #file = self._create_file(original_file_name=conta.complete_file_name, google_file_name=conta.file_name, parent_id=folder_others_base_id)
            file = self._copy_file(file_id=conta.email_file_id, folder_id=folder_others_base_id, file_name=conta.file_name)
            conta.google_file_id = file["id"]

    def upload_ok_list(self, ok_list: List[UtilityBillOkResponse]) -> None:
        total = len(ok_list)
        count = 0
        old_file_id = ''
        old_file_name = ''
        for resp in ok_list:
            count = count + 1

            if resp.utility_bill.tipo_documento == DocumentTypeEnum.CONTA_CONSUMO_RATEIO:
                if old_file_name == resp.nome_calculado:
                    resp.google_file_id = old_file_id
                    continue

            old_file_name = resp.nome_calculado
            if resp.dt_filing:
                data_base = resp.dt_filing
            elif (resp.utility_bill.tipo_documento == DocumentTypeEnum.CONTA_CONSUMO) or \
                    (resp.utility_bill.tipo_documento == DocumentTypeEnum.CONTA_CONSUMO_RATEIO):
                data_base = resp.utility_bill.dt_vencimento if resp.utility_bill.dt_vencimento else resp.utility_bill.dt_emissao
            else:
                data_base = resp.utility_bill.dt_emissao

            dir_name = data_base.strftime('%Y_%m')
            date_folder_id = self._create_folder(dir_name, resp.utility_bill.folder_id)

            google_file_name = resp.nome_calculado
            self._log.save_message(f'Copying file {google_file_name} ({count}/{total})')
            file = self._copy_file(file_id=resp.email_file_id, folder_id=date_folder_id, file_name=google_file_name)
            resp.google_file_id = file["id"]
            old_file_id = resp.google_file_id

            if resp.utility_bill.is_accounting:
                self._log.save_message(f'Copying file {google_file_name} on accounting folder')
                date_folder_id = self._create_folder(dir_name, resp.utility_bill.folder_accounting_id)
                _ = self._copy_file(file_id=resp.email_file_id, folder_id=date_folder_id, file_name=google_file_name)

        return

    def upload_setup_list(self, list: List[UtilityBillBaseResponse]) -> None:
        total = len(list)
        count = 0
        for resp in list:
            count = count + 1
            google_file_name = resp.utility_bill.nome_calculado
            self._log.save_message(f'Copying file {google_file_name} ({count}/{total})')
            file = self._copy_file(file_id=resp.email_file_id, folder_id=resp.utility_bill.folder_setup_id, file_name=google_file_name)
            resp.google_file_id = file["id"]
        return

    def upload_other_list(self, folder_others_base_id: str, all_lists: dict) -> None:
        not_found_list = all_lists['not_found_list']
        error_list = all_lists['error_list']
        duplicate_list = all_lists['duplicate_list']
        ignored_list = all_lists['ignored_list']
        expired_list = all_lists['expired_list']
        
        self._upload_error_list(msg='Copying not found list',folder_others_base_id= folder_others_base_id, error_list=not_found_list)
        self._upload_error_list(msg='Copying error list', folder_others_base_id=folder_others_base_id, error_list=error_list)
        self._upload_error_list(msg='Copying duplicated list', folder_others_base_id=folder_others_base_id, error_list=duplicate_list)
        self._upload_error_list(msg='Copying expired list', folder_others_base_id=folder_others_base_id, error_list=expired_list)
        self._upload_ignored_list(folder_others_base_id, ignored_list)

    def upload_results(self, folder_results_id: str, file_path: str) -> None:
        file_name = os.path.basename(file_path)
        exports_folder_id = self._create_folder('exports', folder_results_id)
        _ = self._create_excel_file(original_file_name=file_path, google_file_name=file_name, parent_id=exports_folder_id)

    def upload_excelfile(self, folder_results_id: str, file_path: str, subfolder_name: str = '', save_previous=False) -> None:
        file_name = os.path.basename(file_path)
        exports_folder_id = self._create_folder(subfolder_name, folder_results_id) if subfolder_name else folder_results_id

        if save_previous:
            now = datetime.datetime.now()
            list_file_name = os.path.splitext(file_name.upper())
            new_file_name = ''
            for i in range(0, len(list_file_name)-1):
                new_file_name += list_file_name[i]
            new_file_name += f'_BACKED_UP_AT_{now.strftime("%Y-%m-%d_%H_%M_%S")}' + list_file_name[len(list_file_name)-1]

            self._save_previous_file(google_file_name=file_name, new_file_name=new_file_name, parent_id=exports_folder_id)

        return  self._create_excel_file(original_file_name=file_path, google_file_name=file_name, parent_id=exports_folder_id)

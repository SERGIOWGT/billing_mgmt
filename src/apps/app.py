from dataclasses import dataclass
import datetime
import os
from src.apps.process_pdf_app import ProcessPdfApp
from src.infra.handlers import ApplicationException, GoogleDriveHandler
from src.infra.repositorios import AccommodationRepository, ConfigurationRepository, ExceptionRepository, PaidBillRepository
from src.infra.repositorios.recorring_errors_repository import RecorringErrorsRepository


@dataclass
class App:
    _log = ''
    _drive: GoogleDriveHandler = ''
    _accommodation_fileid: str = ''
    _local_work_path: str = ''

    def __init__(self, log, drive: GoogleDriveHandler, config_repo: ConfigurationRepository,  accommodation_repo: AccommodationRepository, accommodation_fileid: str, local_work_path: str):
        accommodation_fileid = accommodation_fileid or ''
        ApplicationException.when(accommodation_fileid == '', "'accommodation_fileid' does not exist or empty.", log)
        ApplicationException.when(not os.path.exists(local_work_path), "'local_work_path' does not exist or empty.", log)

        self._log = log
        self._drive = drive
        self._config_repository = config_repo
        self._accommodations_repo = accommodation_repo
        self._local_work_path = local_work_path
        self._accommodation_fileid = accommodation_fileid
        self._permissions_error = []

    def _validate_folder(self, key):
        url = self._get_remote_info(key)
        folder_id = self._drive.extract_id_from_link(url)
        if not folder_id:
            ApplicationException.when(folder_id is None, f'Unable to extract file_id from url. [{key}][{url}]', self._log)

        ApplicationException.when(self._drive.folder_exists(folder_id) is False, f'Folder not found. [{key}]', self._log)
        return folder_id

    def _get_remote_info(self, key) -> str:
        value = self._config_repository.get_key(key)
        ApplicationException.when(value == '', f"Chave não encontrada no arquivo de Configuração. [key='{key}']", self._log)
        return value

    def _validate_folder(self, key):
        url = self._get_remote_info(key)
        folder_id = self._drive.extract_id_from_link(url)
        if not folder_id:
            ApplicationException.when(folder_id is None, f'Unable to extract file_id from url. [{key}][{url}]', self._log)

        ApplicationException.when(self._drive.folder_exists(folder_id) is False, f'Folder not found. [{key}]', self._log)
        return folder_id

    def _check_drive_folders_access(self):
        self._log.save_message("Checking accommodations folder's....", execution=True)
        actual_date = datetime.datetime.now()
        for acc in [acc for acc in self._accommodations_repo.get_activies_accommodations(actual_date)]:
            if acc.folder_id and self._drive.folder_exists(acc.folder_id) is False:
                self._permissions_error.append(
                    f"O folder do Alojamento '{acc.id}' é inexistente ou o robot não tem permissão. [file_id='{acc.folder_id}']")
                acc.folder_permission_error = True

            if acc.folder_accounting_id and self._drive.folder_exists(acc.folder_accounting_id) is False:
                self._permissions_error.append(f"O folder de conciliação do Alojamento '{acc.id}' é inexistente ou o robot não tem permissão. [file_id='{acc.folder_accounting_id}']")
                acc.folder_accounting_permission_error = False

            if acc.folder_setup_id and self._drive.folder_exists(acc.folder_setup_id) is False:
                self._permissions_error.append(f"O folder de setup do Alojamento '{acc.id}' é inexistente ou o robot não tem permissão. [file_id='{acc.folder_setup_id}']")
                acc.folder_setup_permission_error = False

    def _process_files(self):
        others_folder_base_id = self._validate_folder('googledrive.otherfiles.folderid')
        exports_folder_id = self._validate_folder('googledrive.exports.folderid')
        historic_folder_id = self._validate_folder('googledrive.historic.folderid')
        work_folder_id = self._validate_folder('googledrive.work.folderid')
        qd28_folder_id = self._validate_folder('googledrive.qd28.folderid')

        #self._check_drive_folders_access()

        self._log.save_message('Getting exceptions repository....', execution=True)
        stream_file = self._drive.get_google_sheets_file(self._accommodation_fileid)
        except_repo = ExceptionRepository()
        except_repo.from_excel(stream_file)

        self._log.save_message('Getting payments repository....', execution=True)
        paid_repo = PaidBillRepository()
        payments_file_id = self._drive.find_file('database.xlsx', historic_folder_id)
        stream_file = self._drive.get_excel_file(payments_file_id)
        paid_repo.from_excel(stream_file)
        total = paid_repo.number_of_payments()
        self._log.save_message(f'{total} payments(s)', execution=True)

        self._log.save_message('Getting recorring errors repository....', execution=True)
        recorring_repo = RecorringErrorsRepository()
        recorring_file_id = self._drive.find_file('historic_errors.xlsx', historic_folder_id)
        stream_file = self._drive.get_excel_file(recorring_file_id)
        recorring_repo.from_excel(stream_file)
        total = recorring_repo.count()
        self._log.save_message(f'{total} recorring error', execution=True)

        xxx_app = ProcessPdfApp(self._drive, self._log, self._accommodations_repo, paid_repo, except_repo, recorring_repo)
        not_found_list, exports_link = xxx_app.execute(temp_dir=self._local_work_path, email_local_folder='', work_folder_id=work_folder_id, others_folder_base_id=others_folder_base_id,
                                                       exports_folder_id=exports_folder_id, historic_folder_id=historic_folder_id, qd28_folder_id=qd28_folder_id, payments_file_id=payments_file_id,
                                                       recorring_errors_file_id=recorring_file_id)

        return not_found_list, exports_link, self._permissions_error

    def execute(self):
        return self._process_files()
        #return [], '', ''

from dataclasses import dataclass
import os
from src.apps.email_app import EmailApp
from src.apps.process_pdf_app import ProcessPdfApp
from src.infra.email_handler.email_sender_handler import EmailSenderHandler

from src.infra.exception_handler import ApplicationException
from src.infra.google_drive_handler.google_drive_handler import GoogleDriveHandler
from src.infra.repositorios.accommodation_repository import AccommodationRepository
from src.infra.repositorios.configuration_repository import ConfigurationRepository
from src.infra.repositorios.exceptions_repository import ExceptionRepository
from src.infra.repositorios.paid_bill_repository import PaidBillRepository


@dataclass
class App:
    _log = ''
    _drive: GoogleDriveHandler = ''
    _config_repository: ConfigurationRepository = ''
    _accommodation_fileid: str = ''

    _paid_bill_path: str = ''
    _local_work_path: str = ''
    _smtp_server: str = ''
    _imap_server: str = ''
    _user: str = ''
    _password: str = ''

    def _get_config_repository(self, file_id):
        stream_file = self._drive.get_google_sheets_file(file_id)
        config_repo = ConfigurationRepository()
        config_repo.from_excel(stream_file)
        return config_repo

    def _validate_folder(self, key):
        url = self._get_remote_info(key)
        folder_id = self._drive.extract_id_from_link(url)
        if not folder_id:
            ApplicationException.when(folder_id is None, f'Unable to extract file_id from url. [{key}][{url}]', self._log)

        ApplicationException.when(self._drive.folder_exists(folder_id) is False, f'Folder not found. [{key}]', self._log)
        return folder_id

    def __init__(self, log, accommodation_fileid: str, config_path: str, local_work_path: str, paid_bill_path: str):
        ApplicationException.when(accommodation_fileid == '', "'accommodation_fileid' does not exist or empty.", log)
        log.save_message('Connecting google drive....', execution=True)
        self._drive  = GoogleDriveHandler(config_path)

        self._log = log
        self._local_work_path = local_work_path
        self._paid_bill_path = paid_bill_path

        log.save_message('Getting config information...', execution=True)
        self._config_repository = self._get_config_repository(accommodation_fileid)
        total = self._config_repository .number_of_configs()
        log.save_message(f'{total} settings read', execution=True)

        self._imap_server = self._get_remote_info('gmail.imap.server')
        self._smtp_server = self._get_remote_info('gmail.smtp.server')
        self._user = self._get_remote_info('gmail.user')
        self._password = self._get_remote_info('gmail.password')
        self._accommodation_fileid = accommodation_fileid

    def _get_remote_info(self, key) -> str:
        value = self._config_repository.get_key(key)
        ApplicationException.when(value == '', f"Chave não encontrada no arquivo de Configuração. [key='{key}']", self._log)
        return value

    def _get_emails(self):
        input_email_folder = self._get_remote_info('gmail.reading.folder')
        output_email_folder = self._get_remote_info('gmail.output.folder')
        work_folder_id = self._validate_folder('googledrive.work.folderid')

        email_app = EmailApp()
        ApplicationException.when(not os.path.exists(self._local_work_path), f'Path does not exist. [{self._local_work_path}]', self._log)
        email_app.execute(self._drive, self._log, imap_server=self._imap_server, user=self._user, password=self._password,
                          input_email_folder=input_email_folder, output_email_folder=output_email_folder, temp_dir=self._local_work_path,
                            work_folder_id=work_folder_id)

    def _send_warnings(self, not_found_list):
        def __send(list, _to, subject, body):

            if len(list) == 0:
                subject += '- SEM REGISTROS'
                body = 'SEM REGISTROS'
            else:
                body += '\n\n'
                for indx, msg in enumerate(list):
                    body += f'{indx+1}) {msg} \n'
                body += '\n\nFIM DO RELATÓRIO'

            email_sender.send('robotqd23@gmail.com', _to, subject, body)

            return subject, body

        email_list = self._get_remote_info('warning.email.list')
        #email_list = 'financeiro@qualquerdestino.com'
        email_sender = EmailSenderHandler(host=self._smtp_server, user_name=self._user, password=self._password)
        msg_list = [f'{self._drive.make_google_link(x.google_file_id)}' for x in not_found_list]
        __send(msg_list, email_list, "[ROBOT] FATURAS SEM ALOJAMENTOS", 'LISTA DE FATURAS SEM ALOJAMENTOS')

        paid_repo = PaidBillRepository()
        paid_repo.from_excel(self._paid_bill_path)
        erro1 = paid_repo.get_last_discontinuous_period()
        __send(erro1, email_list, "[ROBOT] PAGAMENTOS COM DESCONTINUIDADE", 'LISTA DE ALOJAMENTOS COM DESCONTINUIDADE NOS PAGAMENTOS')

        erro2 = paid_repo.get_possible_faults()
        __send(erro2, email_list, "[ROBOT] FATURAS AINDA NÃO RECEBIDAS", 'LISTA DE ALOJAMENTOS FATURAS PENDENTES')

    def _process_files(self):
        def _validate_folder(key):
            url = self._get_remote_info(key)
            folder_id = self._drive.extract_id_from_link(url)
            if not folder_id:
                ApplicationException.when(folder_id is None, f'Unable to extract file_id from url. [{key}][{url}]', self._log)

            ApplicationException.when(self._drive.folder_exists(folder_id) is False, f'Folder not found. [{key}]', self._log)
            return folder_id

        others_folder_base_id = _validate_folder('googledrive.otherfiles.folderid')
        exports_folder_id = _validate_folder('googledrive.exports.folderid')
        historic_folder_id = _validate_folder('googledrive.historic.folderid')
        work_folder_id = _validate_folder('googledrive.work.folderid')
        qd28_folder_id = _validate_folder('googledrive.qd28.folderid')

        # stream_file = google_drive_handler.get_excel_file(accommodation_fileid)
        stream_file = self._drive.get_google_sheets_file(self._accommodation_fileid)
        except_repo = ExceptionRepository()
        except_repo.from_excel(stream_file)

        self._log.save_message('Getting accommodation repository....', execution=True)
        accommodations_repo = AccommodationRepository()
        accommodations_repo.from_excel(stream_file)
        total = accommodations_repo.number_of_accommodations()
        self._log.save_message(f'{total} accommodation(s)', execution=True)

        self._log.save_message('Getting payments repository....', execution=True)
        paid_repo = PaidBillRepository()
        paid_repo.from_excel(self._paid_bill_path)
        total = paid_repo.number_of_payments()
        self._log.save_message(f'{total} payments(s)', execution=True)

        xxx_app = ProcessPdfApp(self._drive, self._log, accommodations_repo, paid_repo, except_repo)
        not_found_list = xxx_app.execute(temp_dir=self._local_work_path, email_local_folder='', work_folder_id=work_folder_id, others_folder_base_id=others_folder_base_id,
                            exports_folder_id=exports_folder_id, historic_folder_id=historic_folder_id, qd28_folder_id=qd28_folder_id, paid_bill_path=self._paid_bill_path)

        return not_found_list

    def execute(self):
        self._get_emails()
        not_found_list = self._process_files()
        self._send_warnings(not_found_list)

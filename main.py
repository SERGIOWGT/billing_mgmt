import logging
import os
from src.apps.email_app import EmailApp
from src.apps.process_pdf_app import ProcessPdfApp
from src.infra.app_configuration_reader.app_configuration_reader import AppConfigurationReader
from src.infra.application_log.app_log_handler import ApplicationLogHandler
from src.infra.exception_handler import ApplicationException
from src.infra.google_drive_handler.google_drive_handler import \
    GoogleDriveHandler
from src.infra.repositorios.configuration_repository import ConfigurationRepository
from src.infra.repositorios.accommodation_repository import AccommodationRepository
from src.infra.repositorios.exceptions_repository import ExceptionRepository
from src.infra.repositorios.paid_bill_repository import PaidBillRepository


def create_logger(name: str):
    logging.basicConfig(
        # filename="logs/output.txt",
        # filemode="w",
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s",
        datefmt="%Y-%m-%d %I:%M:%S%p",
    )
    return logging.getLogger(name)


def validate_folder(drive, log, config_repo, parent_id, sec_id, sec_name, name):
    config_folder_id = _get_remote_info(config_repo, log, sec_id)
    config_folder_name = _get_remote_info(config_repo, log, sec_name)
    folder_id = drive.find_file(config_folder_name, parent_id)
    ApplicationException.when(folder_id is None, f'{name} folder not found. [{config_folder_name}]')
    ApplicationException.when(config_folder_id != folder_id,
                              f'{name} folder found but its id must be the same as the advisor in "{sec_id}". [{config_folder_id}]')

    return folder_id


def get_local_config_info(key) -> str:
    value = app_config_reader.get(key)
    ApplicationException.when(value == '', f"'{key}' does not exist or empty.")
    return value


def _get_remote_info(configuration_repo, log, key) -> str:
    value = configuration_repo.get_key(key)
    ApplicationException.when(value == '', f"Chave não encontrada no arquivo de Configuração. [key='{key}']", log)
    return value


def config_telegram(log, app_config_reader):
    log.token_execution = app_config_reader.get('telegram_exec_bot_token')
    log.token_warn = app_config_reader.get('telegram_warn_bot_token')
    log.token_error = log.token_execution
    log.list_execution_chat_id = app_config_reader.get('telegram_exec_bot_chats_id')
    log.list_warn_chat_id = app_config_reader.get('telegram_warn_bot_chats_id')


def get_local_config_handler(log, base_dir):
    log.info('App started - Reading local config file...')
    config_path = os.path.join(base_dir, 'config', 'config.json')
    ApplicationException.when(not os.path.exists(config_path), f'Path does not exist. [{config_path}]')
    return AppConfigurationReader(config_path)


def get_drive_handler(log, base_dir):
    log.info('Connecting google drive....', instant_msg=True, warn=True)
    config_directory = os.path.join(base_dir, 'config')
    return GoogleDriveHandler(config_directory)


def get_config_repository(log, drive, file_id):
    log.info('Getting accommodation repository....', instant_msg=True, warn=True)
    #stream_file = drive.get_excel_file(file_id)
    stream_file = drive.get_google_sheets_file(file_id)
    config_repo = ConfigurationRepository()
    config_repo.from_excel(stream_file)
    return config_repo


if __name__ == '__main__':
    erro = False
    config_repo = None
    accommodation_fileid = ''
    email_local_folder = ''
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log = ApplicationLogHandler(create_logger(__name__))

    try:
        app_config_reader = get_local_config_handler(log, base_dir)
        google_drive_handler = get_drive_handler(log, base_dir)
        local_email_work_folder = get_local_config_info('email_in_local_folder')
        if (local_email_work_folder):
            email_local_folder = os.path.join(base_dir, '.email_work_folder')

        config_telegram(log, app_config_reader)
        accommodation_fileid = get_local_config_info('google_drive_accommodation_fileid')
        config_repo = get_config_repository(log, google_drive_handler, accommodation_fileid)

    except Exception as error:
        msg = str(error)
        log.error(msg)
        log.info('App Finished', instant_msg=True, warn=True)
        exit(1)

    if not (local_email_work_folder):
        try:
            smtp_server = _get_remote_info(config_repo, log, 'gmail.imap.server')
            user = _get_remote_info(config_repo, log, 'gmail.user')
            password = _get_remote_info(config_repo, log, 'gmail.password')
            input_email_folder = _get_remote_info(config_repo, log, 'gmail.reading.folder')
            output_email_folder = _get_remote_info(config_repo, log, 'gmail.output.folder')
            work_folder_id = _get_remote_info(config_repo, log, 'googledrive.work.folderid')

            email_app = EmailApp()
            temp_dir = os.path.join(base_dir, 'temp')
            ApplicationException.when(not os.path.exists(temp_dir), f'Path does not exist. [{temp_dir}]', log)
            email_app.execute(google_drive_handler, log, smtp_server=smtp_server, user=user, password=password,
                              input_email_folder=input_email_folder, output_email_folder=output_email_folder, temp_dir=temp_dir,
                              work_folder_id=work_folder_id)

        except Exception as error:
            msg = str(error)
            log.error(msg)
            log.info('App Finished', instant_msg=True, warn=True)
            exit(2)

    # try:
    folder_base_id = _get_remote_info(config_repo, log, 'googledrive.base.folderid')
    if folder_base_id.upper() in ['VAZIO', 'RAIZ']:
        folder_base_id = ''

    others_folder_base_id = validate_folder(google_drive_handler, log, config_repo, folder_base_id, 'googledrive.otherfiles.folderid', 'googledrive.otherfiles.foldername', 'Other files')
    results_folder_id = validate_folder(google_drive_handler, log, config_repo, folder_base_id, 'googledrive.results.folderid', 'googledrive.results.foldername', 'Results')
    work_folder_id = validate_folder(google_drive_handler, log, config_repo, folder_base_id, 'googledrive.work.folderid', 'googledrive.work.foldername', 'Work')

    #stream_file = google_drive_handler.get_excel_file(accommodation_fileid)
    stream_file = google_drive_handler.get_google_sheets_file(accommodation_fileid)
    except_repo = ExceptionRepository()
    except_repo.from_excel(stream_file)

    accommodations_repo = AccommodationRepository()
    accommodations_repo.from_excel(stream_file)

    paid_repo = PaidBillRepository()
    paid_bill_path = os.path.join(base_dir, 'database', 'database.xlsx')
    qd28_path = os.path.join(base_dir,'database', '#QD28_IMPORTACAO_ROBOT.xlsx')
    #paid_repo.from_excel(paid_bill_path)
    exports_folder = os.path.join(base_dir, 'exports')

    xxx_app = ProcessPdfApp(google_drive_handler, log, accommodations_repo, paid_repo, except_repo)
    xxx_app.execute(work_folder_id=work_folder_id, email_local_folder=email_local_folder, others_folder_base_id=others_folder_base_id,
                    results_folder_id=results_folder_id, qd28_path=qd28_path, paid_bill_path=paid_bill_path, exports_folder=exports_folder)

    # except Exception as error:
    #    msg = str(error)
    #    log.error(msg)
    #    log.info('App Finished', instant_msg=True, warn=True)
    #    exit()


import datetime
import logging
import os
from src.apps.app import App
from src.apps.email_app.email_app import EmailApp
from src.apps.email_app.email_app_dto import EmailAppDto
from src.apps.send_warning_app import SendWarningApp
from src.infra.handlers import AppConfigurationReader, ApplicationException, GoogleDriveHandler
from src.infra.handlers.email_sender_handler import EmailSenderHandler
from src.infra.handlers.log.app_database_log import ApplicationDatabaseLogHandler
from src.infra.repositorios.accommodation_repository import AccommodationRepository
from src.infra.repositorios.configuration_repository import ConfigurationRepository


def get_local_config_info(app_config_reader, key) -> str:
    value = app_config_reader.get(key)
    ApplicationException.when(value == '', f"'{key}' does not exist or empty.")
    return value

def get_remote_config_info(file_id: str, drive: GoogleDriveHandler):
    stream_file = drive.get_google_sheets_file(file_id)
    config_repo = ConfigurationRepository()
    config_repo.from_excel(stream_file)
    return config_repo

def get_remote_info_from_config(config_repository: ConfigurationRepository, key) -> str:
    value = config_repository.get_key(key)
    ApplicationException.when(value == '', f"Chave não encontrada no arquivo de Configuração. [key='{key}']")
    return value

def get_email_credentials(config_repository: ConfigurationRepository) -> tuple:
    imap_server = get_remote_info_from_config(config_repository, 'gmail.imap.server')
    smtp_server = get_remote_info_from_config(config_repository, 'gmail.smtp.server')
    user = get_remote_info_from_config(config_repository, 'gmail.user')
    password = get_remote_info_from_config(config_repository, 'gmail.password')

    return (imap_server, smtp_server, user, password)

def get_email_others_infos(config_repo: ConfigurationRepository) -> tuple:
    _input_email_folder = get_remote_info_from_config(config_repo, 'gmail.reading.folder')
    _output_email_folder = get_remote_info_from_config(config_repo, 'gmail.output.folder')
    _work_folder_id = get_remote_info_from_config(config_repo, 'googledrive.work.folderid')

    return _input_email_folder, _output_email_folder, _work_folder_id


def get_email_sender(config_repo: ConfigurationRepository):
    (_, host, user, password) = get_email_credentials(config_repo)
    return EmailSenderHandler(host=host, user_name=user, password=password)


def configure_initial_paths(log, base_dir):
    log.save_message('App started - Reading local config file...', execution=True)
    _config_path = os.path.join(base_dir, 'config')
    _config_file_path = os.path.join(_config_path, 'config.json')
    ApplicationException.when(not os.path.exists(_config_path), f'Path does not exist. [{_config_file_path}]')
    _local_work_path = os.path.join(base_dir, 'temp')
    ApplicationException.when(not os.path.exists(_local_work_path), "'local_work_path' does not exist or empty.")
    return _config_path, _config_file_path, _local_work_path


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    #log = ApplicationLogHandler(create_logger(__name__))
    log = ApplicationDatabaseLogHandler(__name__)

    email_sender = None
    try:
        config_path, config_file_path, local_work_path = configure_initial_paths(log, base_dir)
        app_config_reader = AppConfigurationReader(config_file_path)
        ApplicationException.when(not os.path.exists(local_work_path), f'Path does not exist. [{local_work_path}]')

        log.save_message('Connecting google drive....', execution=True)
        drive = GoogleDriveHandler(config_path)

        log.save_message('Getting local configuration repository....', execution=True)
        accommodation_fileid = get_local_config_info(app_config_reader, 'google_drive_accommodation_fileid') or ''
        ApplicationException.when(accommodation_fileid == '', "'accommodation_fileid' does not exist or empty.")

        log.save_message('Getting remote config information...', execution=True)
        config_repository = get_remote_config_info(accommodation_fileid, drive)
        email_sender = get_email_sender(config_repo=config_repository)
        email_list = get_remote_info_from_config(config_repository, 'warning.email.list')

        (_, host, user, password) = get_email_credentials(config_repository)
        (input_email_folder, output_email_folder, work_folder_id) = get_email_others_infos(config_repository)
        work_folder_id = drive.extract_id_from_link(work_folder_id)
        email_app_dto = EmailAppDto(imap_server=host, user=user, password=password, input_email_folder=input_email_folder,
                                    output_email_folder=output_email_folder, temp_dir=local_work_path, work_folder_id=work_folder_id)

        email_app = EmailApp()
        email_app.execute(drive, log, email_app_dto)

        log.save_message('Getting accommodation repository....', execution=True)
        stream_file = drive.get_google_sheets_file(accommodation_fileid)
        accommodation_repo = AccommodationRepository()
        accommodation_repo.from_excel(stream_file)

        app = App(log, drive=drive, config_repo=config_repository, accommodation_repo=accommodation_repo, accommodation_fileid=accommodation_fileid, local_work_path=local_work_path)
        not_found_list, exports_file_link, permission_error = app.execute()
        active_accs = accommodation_repo.get_activies_id(datetime.datetime.now())

        days_to_warning = get_remote_info_from_config(config_repository, 'days.to.warning')
        historic_folder_id = drive.extract_id_from_link(get_remote_info_from_config(config_repository, 'googledrive.historic.folderid'))

        log.save_message('Connecting email...', execution=True)
        sender_warning = SendWarningApp(drive=drive, log=log, email_sender=email_sender)
        sender_warning.execute(not_found_list, permission_error, active_accs, historic_folder_id,  exports_file_link, email_list, days_to_warning)

    except Exception as error:
        log.save_message(str(error), error=True)
        if email_sender:
            for email_address in email_list.split(','):
                email_sender.send('robotqd23@gmail.com', email_address, 'Execution error', str(error))
        else:
            raise error

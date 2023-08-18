import logging
import os
from src.apps.app import App
from src.infra.app_configuration_reader.app_configuration_reader import AppConfigurationReader
from src.infra.application_log.app_log_handler import ApplicationLogHandler
from src.infra.exception_handler import ApplicationException
from src.infra.google_drive_handler.google_drive_handler import GoogleDriveHandler

def create_logger(name: str):
    logging.basicConfig(
        # filename="logs/output.txt",
        # filemode="w",
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s",
        datefmt="%Y-%m-%d %I:%M:%S%p",
    )
    return logging.getLogger(name)

def get_local_config_info(app_config_reader, key) -> str:
    value = app_config_reader.get(key)
    ApplicationException.when(value == '', f"'{key}' does not exist or empty.")
    return value

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log = ApplicationLogHandler(create_logger(__name__))

    #try:
    log.save_message('App started - Reading local config file...', execution=True)
    config_path = os.path.join(base_dir, 'config')
    config_file_path = os.path.join(config_path, 'config.json')
    ApplicationException.when(not os.path.exists(config_path), f'Path does not exist. [{config_file_path}]')
    app_config_reader = AppConfigurationReader(config_file_path)
    local_work_path = os.path.join(base_dir, 'temp')

    log.save_message('Getting configuration repository....', execution=True)
    accommodation_fileid = get_local_config_info(app_config_reader, 'google_drive_accommodation_fileid')
    local_email_work_folder = get_local_config_info(app_config_reader, 'email_in_local_folder')
    paid_bill_path = os.path.join(base_dir, 'database', 'database.xlsx')

    log.save_message('Connecting google drive....', execution=True)
    drive = GoogleDriveHandler(config_path)
    app = App(log, accommodation_fileid=accommodation_fileid, drive=drive, local_work_path=local_work_path, paid_bill_path=paid_bill_path)
    app.execute()

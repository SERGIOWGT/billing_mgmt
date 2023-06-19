import logging
import os

from src.app import App
from src.infra.app_configuration_reader.app_configuration_reader import \
    AppConfigurationReader
from src.infra.application_log.app_log_handler import ApplicationLogHandler
from src.infra.exception_handler import ApplicationException
from src.infra.google_drive_handler.google_drive_handler import \
    GoogleDriveHandler


def create_logger(name: str):
    logging.basicConfig(
        # filename="logs/output.txt",
        # filemode="w",
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s",
        datefmt="%Y-%m-%d %I:%M:%S%p",
    )

    return logging.getLogger(name)


def check_config_session(key) -> str:
    value = app_config_reader.get(key)
    ApplicationException.when(value == '', f"'{key}' does not exist or empty.")
    return value


if __name__ == '__main__':
    try:
        log = ApplicationLogHandler(create_logger(__name__))
        log.info('App started')
        log.info('Reading local config file')
        config_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
        config_path = os.path.join(config_directory, 'config.json')
        ApplicationException.when(not os.path.exists(config_path), f'Path does not exist. [{config_path}]')
        app_config_reader = AppConfigurationReader(config_path)
        accommodation_fileid = check_config_session('google_drive_accommodation_fileid')

        log.token_execution = app_config_reader.get('telegram_exec_bot_token')
        log.token_warn = app_config_reader.get('telegram_warn_bot_token')
        log.token_error = log.token_execution
        log.list_execution_chat_id = app_config_reader.get('telegram_exec_bot_chats_id')
        log.list_warn_chat_id = app_config_reader.get('telegram_warn_bot_chats_id')
        work_directory = app_config_reader.get('work_directory')

        log.info('App started', instant_msg=True, warn=True)
        google_drive_handler = GoogleDriveHandler(config_directory)
        log.info('Google drive connected', instant_msg=True)

        app = App(work_directory, accommodation_fileid, google_drive_handler, log)
        app.execute()

    except Exception as error:
        msg = str(error)
        log.error(msg)
        print(msg)

        log.info('App Finished', instant_msg=True, warn=True)


# qrsatvqbzwoddmbj

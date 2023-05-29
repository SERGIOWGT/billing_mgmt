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

def check_config_session(app_config_reader, key)->str:
    value = app_config_reader.get(key)
    ApplicationException.when(value == '', f"'{key}' does not exist or empty.")
    return value


def create_app_config(log, config_directory):
    config_path = os.path.join(config_directory, 'config.json')
    ApplicationException.when(not os.path.exists(config_path), f'Path does not exist. [{config_path}]', log)
    return AppConfigurationReader(config_path)


def create_temp_folder():
    temporary_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
    if os.path.exists(temporary_folder):
        os.path.create(temporary_folder)
 
def config_chatbot_telegram(log, app_config):
    log.token_execution = app_config.get('telegram_exec_bot_token')
    log.token_warn = app_config.get('telegram_warn_bot_token')
    log.token_error = log.token_execution
    if (log.token_execution):
        log.list_execution_chat_id = app_config.get('telegram_exec_bot_chats_id')
    if (log.token_warn):
        log.list_warn_chat_id = app_config.get('telegram_warn_bot_chats_id')
 
if __name__ == '__main__':
    try:
        log = ApplicationLogHandler(create_logger(__name__))
        log.info('App started')
        config_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
        app_config_reader = create_app_config(log, config_directory)

        accommodation_fileid=app_config_reader.get('google_drive_accommodation_fileid')
        ApplicationException.when(accommodation_fileid == '', "'google_drive_accommodation_fileid' does not exist or empty.")
        config_chatbot_telegram(log, app_config_reader)

        log.info('App started', instant_msg=True, warn=True)
        google_drive_handler = GoogleDriveHandler(config_directory)
        log.info('Google drive connected', instant_msg=True)
        
        #file_id = '18aA4iHaeLuv89HMec8s9CBmza7agMz3W'
        #source_folder_id = '1a0nD8Gf5lNsdW-jc78NfDuBxBtUTyb0V'
        #destination_folder_id = '1IPpfas07UXImOU7kAofwRDbPvg2gFURV'
        #new_file_name = 'new_file_name.pdf'

        # Retrieve the current parents of the file
        #response = google_drive_handler._drive.files().get(fileId=file_id, fields='parents').execute()
        #previous_parents = ",".join(response.get('parents'))

        # Update the file name
        #google_drive_handler._drive.files().update(
        #    fileId=file_id,
        #    body={'name': new_file_name},
        #    fields='id, name'
        #).execute()

        # Move the file to the destination folder
        #google_drive_handler._drive.files().update(
        #    fileId=file_id,
        #    addParents=destination_folder_id,
        #    removeParents=previous_parents,
        #    fields='id, parents'
        #).execute()
        
        temporary_folder = ""
        app = App(temporary_folder, accommodation_fileid, google_drive_handler, log)
        app.execute()

    except Exception as error:
        msg = str(error)
        log.info(msg)
        log.info('App Finished', instant_msg=True, warn=True)


# qrsatvqbzwoddmbj

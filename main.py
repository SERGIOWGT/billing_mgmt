import logging
import os
from src.infra.application_log.app_log_handler import ApplicationLogHandler
from src.infra.google_drive_handler.google_drive_handler import GoogleDriveHandler
from src.infra.app_configuration_reader.app_configuration_reader import AppConfigurationReader
from src.app import App


def create_logger(name: str):
    logging.basicConfig(
        # filename="logs/output.txt",
        # filemode="w",
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s",
        datefmt="%Y-%m-%d %I:%M:%S%p",
    )

    return logging.getLogger(name)


def get_accommodation_file_id() -> None:
    log.info('Local config file read', instant_msg=True)
    app_config_reader = AppConfigurationReader(os.path.join(config_directory, 'config.json'))
    return app_config_reader.get('google_drive_accommodation_fileid')

if __name__ == '__main__':
    #try:
        _log = create_logger(__name__)

        log = ApplicationLogHandler(_log)

        log.info('App started', instant_msg=True, warn=True)
        config_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')

        google_drive_handler = GoogleDriveHandler(config_directory)
        log.info('Google drive connected', instant_msg=True)

        app = App(get_accommodation_file_id(), google_drive_handler, log)
        app.execute()

    #except Exception as error:
    #    msg = str(error)
    #    log.critical(msg)
    #    print(msg)

        log.info('App Finished', instant_msg=True, warn=True)


# qrsatvqbzwoddmbj

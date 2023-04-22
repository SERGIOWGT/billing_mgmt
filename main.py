import logging
import os
from src.infra.google_drive_handler.google_drive_handler import GoogleDriveHandler
from src.infra.app_configuration_reader.app_configuration_reader import AppConfigurationReader
from src.app import App

def create_logger(name: str):
    logging.basicConfig(
        #filename="logs/output.txt",
        #filemode="w",
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s",
        datefmt="%Y-%m-%d %I:%M:%S%p",
    )

    return logging.getLogger(name)

if __name__ == '__main__':
    log = create_logger(__name__)
    log.info('App started')

    #try:
    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
    app_config = AppConfigurationReader(os.path.join(config_dir, 'config.json'))
    log.info('Config file read')

    drive = GoogleDriveHandler(config_dir)
    log.info('Google drive connected')

    app = App(app_config, drive, log)
    app.execute()

    #except Exception as error:
    #    msg = str(error)
    #    log.critical(msg)
    #    print(msg)

import logging
from dotenv import load_dotenv
from src.domain.entities.alojamentos import PoolAlojamentos
from src.infra.excel_reader import ExcelReader
from src.infra.gdrive_handler import GDriveHandler
from src.infra.exception_handler import ApplicationException
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


    try:
        config = ConfigurationApp('config\\config.json')
        drive = GoogleDriveHandler(config.get("directories.config"))
        log.info('Google Drive connected')

        app = App(config, log, drive)
        app.execute()

    except Exception as error:
        msg = str(error)
        log.critical(msg)
        print(msg)
  
    try:
        alojamentos = ExcelReader().get_database('Alojamentos.xlsx')        
        app.process_downloaded_files(log, PoolAlojamentos(alojamentos))
    except Exception as error:
        msg = str(error)
        log.critical(msg)
        print(msg)

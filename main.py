import os
import logging
from dotenv import load_dotenv
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

def get_environ_vars():
    return (os.environ.get('IMAP_SERVER', ''), 
                os.environ.get('USER_EMAIL', ''), 
                os.environ.get('PASS_EMAIL', ''),  
                os.environ.get('BASE_FOLDER', ''),     
                os.environ.get('EMAIL_DESTINATION_FOLDER', ''))

if __name__ == '__main__':
    load_dotenv()

    log = create_logger(__name__)
    log.info('Init App')
    imap_server, user_name, password, base_folder, email_destination_folder = get_environ_vars()
    log.info('Environment vars read')
    download_folder = os.path.join(base_folder, 'downloads')

    app = App(download_folder)
    try:
        ApplicationException.when(not os.path.exists(download_folder), f'Path does not exist. [{download_folder}]', log)

        count_email = app.download_files(imap_server, user_name, password, download_folder)
        if count_email == 0:
            print('Nenhum arquivo baixado')
        elif count_email == 1:
            print('Um arquivo baixado')
        else:
            print(f'{count_email} arquivos baixados')

    except Exception as error:
        msg = str(error)
        log.critical(msg)
        print(msg)

    try:
        app.process_downloaded_files(log)
    except Exception as error:
        msg = str(error)
        log.critical(msg)
        print(msg)

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
    msg = 'App started'
    log.info(msg)
    print(msg)
    imap_server, user_name, password, base_folder, email_destination_folder = get_environ_vars()
    
    msg = 'Environment vars read'
    log.info(msg)
    print(msg)
        
    try:
        app = App(base_folder, log)
        app.execute(imap_server, user_name, password)

    except Exception as error:
        msg = str(error)
        log.critical(msg)
        print(msg)

    msg = 'App finished'
    log.info(msg)
    print(msg)
import logging
from src.infra.app_configuration import ConfigurationApp
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
    msg = 'App started'
    log.info(msg)
    try:
        config = ConfigurationApp('config\\config.json')
        app = App(config, log)
        app.execute()

    except Exception as error:
        msg = str(error)
        log.critical(msg)
        print(msg)

    msg = 'App finished'
    log.info(msg)
    print(msg)

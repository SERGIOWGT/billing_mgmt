import os
from dotenv import load_dotenv
from src.infra.exception_handler import ApplicationException
from src.app import App

if __name__ == '__main__':
    load_dotenv()
    imap_server=os.environ.get('IMAP_SERVER', '')
    user_name = os.environ.get('USER_EMAIL', '')
    password = os.environ.get('PASS_EMAIL', '')
    base_folder=os.environ.get('BASE_FOLDER', '')
    email_destination_folder = os.environ.get('EMAIL_DESTINATION_FOLDER', '')
    download_folder = os.path.join(base_folder, 'downloads')
    
    app = App(download_folder)

    try:
        ApplicationException.when(not os.path.exists(download_folder), f'Path does not exist. [{download_folder}]')
        count_email = app.download_files(imap_server, user_name, password, download_folder)
        if count_email == 0:
            print('Nenhum arquivo baixado')
        elif count_email == 1:
            print('Um arquivo baixado')
        else:
            print(f'{count_email} arquivos baixados')

    except Exception as error:
        print(str(error))

    try:
        app.process_downloaded_files()
    except Exception as error:
        print(str(error))

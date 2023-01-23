import os
from dotenv import load_dotenv
from src.app import App

if __name__ == '__main__':
    load_dotenv()
    imap_server=os.environ.get('IMAP_SERVER', '')
    user_name = os.environ.get('USER_EMAIL', '')
    password = os.environ.get('PASS_EMAIL', '')
    base_folder=os.environ.get('BASE_FOLDER', '')
    download_folder = os.path.join(base_folder, 'downloads')
    
    # testar se o folder existe
    
    App.execute(imap_server, user_name, password, download_folder)

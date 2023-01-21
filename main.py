from src.app import App 
from dotenv import load_dotenv
import os

if __name__ == '__main__':
    load_dotenv()
    user_name = os.environ.get('USER_EMAIL', '')
    password = os.environ.get('PASS_EMAIL', '')

    App.execute(user_name, password)
    
import os
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


def create_empty_directories():
    # Lista de diretórios vazios a serem criados
    directories = [
        'logs',
        'config',
        'database',
        'downloads',
        'exports',
        'sample-files'
    ]

    # Criação dos diretórios vazios
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


create_empty_directories()

setup(
    name='Robot_QQDestino',
    version='1.0',
    description='',
    author='',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    data_files=[
        ('', ['read.me']),
        ('', ['requirements.txt']),
        ('', ['main.py']),
        ('config', ['config/client_secret.json']),
        ('sample-files', ['sample-files/config.json-sample']), 
        ('sample-files', ['sample-files/Alojamentos-sample.xlsx']),
        ('src', ['src/app.py']),
        ('', ['main.py'])
    ],
    setup_requires=[
        'google-api-python-client',
        'oauth2client',
    ],
    install_requires=requirements,
)

import os

from src.infra.google_drive_handler.google_drive_handler import GoogleDriveHandler
from src.infra.repositorios.configuration_repository import ConfigurationRepository
from src.infra.repositorios.repositorio_alojamentos import AccommodationRepository


def main() -> None:
    config_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
    google_drive_handler = GoogleDriveHandler(config_directory)
    stream_file = google_drive_handler.get_excel_file('17v8tIuBigfmTWrjdkCiREZ1YwW0dTXU9')

    config_repo = ConfigurationRepository()
    config_repo.from_excel(stream_file)
    acc_repo = AccommodationRepository()
    acc_repo.from_excel(stream_file)


main()

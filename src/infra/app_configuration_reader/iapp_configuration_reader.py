from abc import ABC, abstractmethod

class IAppConfigurationReader(ABC):
    @abstractmethod
    def get(self, key_name: str) -> dict:
        ...

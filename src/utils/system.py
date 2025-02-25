import os
from abc import ABC, abstractmethod


class SystemCleaner(ABC):
    @abstractmethod
    def clear(self) -> None:
        pass


class WindowsCleaner(SystemCleaner):
    def clear(self) -> None:
        os.system('cls')


class SystemManager:
    @staticmethod
    def get_cleaner() -> SystemCleaner:
        return WindowsCleaner()

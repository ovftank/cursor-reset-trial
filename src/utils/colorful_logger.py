import logging
import os
from datetime import datetime

if os.name == 'nt':
    os.system('color')


class ColorfulLogger:
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    RESET = '\033[0m'

    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(name)
        self.formatter = logging.Formatter(
            '%(color)s%(message)s%(reset)s',
            defaults={'reset': self.RESET}
        )

        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self.formatter)
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.INFO)

    def _log(self, color: str, message: str) -> None:
        time = datetime.now().strftime('%H:%M:%S')
        self.logger.info(
            message,
            extra={'color': color, 'time': time}
        )

    def info(self, message: str) -> None:
        self._log(self.BLUE, message)

    def success(self, message: str) -> None:
        self._log(self.GREEN, message)

    def warning(self, message: str) -> None:
        self._log(self.YELLOW, message)

    def error(self, message: str) -> None:
        self._log(self.RED, message)

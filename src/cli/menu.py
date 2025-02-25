from typing import Callable, Dict

import questionary

from src.utils.console import ConsoleManager
from src.utils.system import SystemManager


class Menu:
    def __init__(self, console_manager: ConsoleManager):
        self.console = console_manager
        self.cleaner = SystemManager.get_cleaner()
        self.style = questionary.Style([
            ('qmark', 'fg:cyan bold'),
            ('question', 'bold'),
            ('pointer', 'fg:cyan bold'),
            ('highlighted', 'fg:ansibrightgreen bold'),
            ('selected', 'fg:blue'),
            ('instruction', ''),
            ('bottom-toolbar', '')
        ])

    def show(self, choices: Dict[str, Callable]):
        while True:
            try:
                self.cleaner.clear()
                self.console.print_welcome()

                choice = questionary.select(
                    "Chọn chức năng:",
                    choices=list(choices.keys()),
                    style=self.style
                ).ask()

                if choice is None:
                    self.cleaner.clear()
                    self.console.print_goodbye()
                    break

                if choice == "Thoát":
                    self.cleaner.clear()
                    self.console.print_goodbye()
                    break

                self.cleaner.clear()
                choices[choice]()
                input("\nNhấn Enter để tiếp tục...")

            except KeyboardInterrupt:
                self.cleaner.clear()
                self.console.print_goodbye()
                break

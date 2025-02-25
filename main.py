from src.cli.app import CursorManagerCLI
from src.utils.console import ConsoleManager

if __name__ == "__main__":
    console = ConsoleManager()
    cli = CursorManagerCLI()
    try:
        cli.run()
    except KeyboardInterrupt:
        console.clear_line()
        console.print_goodbye()

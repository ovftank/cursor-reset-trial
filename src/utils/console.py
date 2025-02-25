from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class ConsoleManager:
    def __init__(self):
        self.console = Console()

    def clear_line(self):
        print('\r\033[K', end='')

    def print_welcome(self):
        self.console.print(Panel.fit(
            "[bold bright_green]Cursor Manager CLI[/]\n[dim]Sử dụng --help để xem hướng dẫn[/]",
            border_style="bright_green"
        ))

    def print_goodbye(self):
        self.console.print("[bright_green]Tạm biệt![/]")

    def print_version(self, version: str):
        panel = Panel(
            f"[bold bright_blue]Phiên bản Cursor:[/] [bright_green]{version}[/]",
            title="[bright_green]Thông tin[/]",
            border_style="bright_green"
        )
        self.console.print(panel)

    def print_status_table(self, data: dict):
        table = Table(title="Trạng thái Cursor", border_style="bright_green")
        table.add_column("Thông số", style="bright_blue", no_wrap=True)
        table.add_column("Giá trị", style="bright_green")

        for key, value in data.items():
            table.add_row(key, value)

        self.console.print(table)

    def print_error(self, message: str):
        self.console.print(f"[bold red]Lỗi:[/] {message}")

    def print_success(self, message: str):
        self.console.print(f"[bright_green]✓[/] {message}")

    def print_failure(self, message: str):
        self.console.print(f"[bold red]✗[/] {message}")

    def print_info(self, message: str):
        self.console.print(f"[bold blue]ℹ[/] {message}")

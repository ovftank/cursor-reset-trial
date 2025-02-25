import os

import questionary

from src.utils.colorful_logger import ColorfulLogger


class BrowserHandler:
    def __init__(self):
        self.logger = ColorfulLogger(__name__)
        self.style = questionary.Style([
            ('qmark', 'fg:cyan bold'),
            ('question', 'bold'),
            ('pointer', 'fg:cyan bold'),
            ('highlighted', 'fg:ansibrightgreen bold'),
            ('selected', 'fg:blue')
        ])

    def open_auth_page(self) -> bool:
        try:
            answer = questionary.confirm(
                "Bạn có muốn đăng nhập lại Cursor không?",
                default=True,
                style=self.style
            ).ask()

            if answer:
                self.logger.info("Đang mở trình duyệt...")
                os.system('start https://authenticator.cursor.sh/')
                self.logger.success("Hoàn tất!")
                return True
            return False

        except Exception as e:
            self.logger.error(f"Lỗi: {e}")
            return False

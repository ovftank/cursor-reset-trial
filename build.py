import subprocess
import sys
from pathlib import Path


def create_executable():
    if sys.platform.startswith('win'):
        sys.stdout.reconfigure(encoding='utf-8')

    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)

    icon = str(images_dir / "icon.ico")
    icon_mac = str(images_dir / "icon.icns")

    # Kiểm tra file icon tồn tại
    if sys.platform.startswith('win') and not Path(icon).exists():
        print(f"Lỗi: Không tìm thấy file icon tại {icon}")
        sys.exit(1)
    elif sys.platform.startswith('darwin') and not Path(icon_mac).exists():
        print(f"Lỗi: Không tìm thấy file icon tại {icon_mac}")
        sys.exit(1)

    # Cấu hình cơ bản cho cả Windows và macOS
    pyinstaller_command = [
        'pyinstaller',
        '--noconfirm',
        '--onefile',
        '--windowed',
        '--clean',
        '--name', 'CursorResetTrial',
        'src/__main__.py'
    ]

    # Thêm cấu hình riêng cho từng hệ điều hành
    if sys.platform.startswith('win'):
        pyinstaller_command.extend([
            '--uac-admin',
            '--icon', icon,
            '--add-data', f'{icon};.',
            '--add-data', f'{icon};images'
        ])
    elif sys.platform.startswith('darwin'):
        pyinstaller_command.extend([
            '--icon', icon_mac,
            '--add-data', f'{icon_mac}:.',
            '--add-data', f'{icon_mac}:images',
            '--target-architecture', 'universal2'
        ])

    try:
        result = subprocess.run(pyinstaller_command,
                              capture_output=True,
                              text=True,
                              encoding='utf-8')

        if result.returncode == 0:
            output_file = Path('dist/CursorResetTrial.exe' if sys.platform.startswith('win')
                             else 'dist/CursorResetTrial.app')
            if output_file.exists():
                print("Build thành công!")
                print(f"File thực thi được tạo tại: {output_file}")
            else:
                print("Lỗi: File thực thi không được tạo")
                sys.exit(1)
        else:
            print("Lỗi khi build:")
            print(result.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    create_executable()

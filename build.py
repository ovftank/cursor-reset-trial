import subprocess
import sys
from pathlib import Path


def create_executable():
    if sys.platform.startswith('win'):
        sys.stdout.reconfigure(encoding='utf-8')

    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)

    icon = str(images_dir / "icon.ico")

    if not Path(icon).exists():
        print(f"Lỗi: Không tìm thấy file icon tại {icon}")
        sys.exit(1)

    pyinstaller_command = [
        'pyinstaller',
        '--noconfirm',
        '--onefile',
        '--windowed',
        '--uac-admin',
        '--clean',
        '--icon', icon,
        '--add-data', f'{icon};.',
        '--add-data', f'{icon};images',
        '--name', 'CursorResetTrial',
        'src/__main__.py'
    ]

    try:
        result = subprocess.run(pyinstaller_command,
                                capture_output=True,
                                text=True,
                                encoding='utf-8')

        if result.returncode == 0:
            output_file = Path('dist/CursorResetTrial.exe')
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

import subprocess


def create_executable():
    icon = "images/icon.ico"
    pyinstaller_command = [
        'pyinstaller',
        '--noconfirm',
        '--onefile',
        '--windowed',
        '--icon', icon,
        '--add-data', f'{icon};.',
        'main.py'
    ]
    result = subprocess.run(pyinstaller_command,
                            capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)


if __name__ == '__main__':
    create_executable()

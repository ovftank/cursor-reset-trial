from pathlib import Path

import PyInstaller.__main__

current_dir = Path(__file__).parent

icon_path = current_dir / "icon.ico"
main_script = current_dir / "src" / "cli" / "app.py"

dist_dir = current_dir / "dist"
dist_dir.mkdir(exist_ok=True)

PyInstaller.__main__.run([
    str(main_script),
    '--name=cursor-manager',
    '--onefile',
    '--console',
    '--clean',
    f'--distpath={dist_dir}',
    '--add-data=src;src',
    f'--icon={icon_path}' if icon_path.exists() else None,
])

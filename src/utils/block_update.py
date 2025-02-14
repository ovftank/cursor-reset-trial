import os
import shutil
import subprocess

import psutil
import requests

from src.config.translations import DEFAULT_TRANSLATIONS

CURSOR_DOWNLOAD_URL = "https://downloader.cursor.sh/builds/250103fqxdt5u9z/windows/nsis/x64"
TOTAL_SIZE = 127058248  # Size in bytes


def get_cursor_version():
    try:
        result = subprocess.run('cursor --version',
                                shell=True,
                                capture_output=True,
                                text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            commit = result.stdout.split('\n')[1]
            arch = result.stdout.split('\n')[2]
            return {
                'version': version,
                'commit': commit,
                'architecture': arch
            }
    except Exception:
        return None


def kill_cursor_processes():
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() == 'cursor.exe':
                proc.kill()
    except Exception:
        pass


def download_with_progress(url, path, progress_callback, translations):
    response = requests.get(url, stream=True)
    downloaded_size = 0

    with open(path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded_size += len(chunk)
                progress = (downloaded_size / TOTAL_SIZE) * 100
                progress_callback(
                    translations['downloading_progress'].format(progress))


def download_and_install_cursor(progress_callback=None, translations=None):
    if progress_callback is None:
        def progress_callback(_): return None

    if translations is None:
        translations = DEFAULT_TRANSLATIONS

    temp_dir = os.path.join(os.getenv('TEMP'), 'cursor_installer')
    os.makedirs(temp_dir, exist_ok=True)
    installer_path = os.path.join(temp_dir, 'cursor_setup.exe')

    try:
        progress_callback(translations['closing_cursor'])
        kill_cursor_processes()

        progress_callback(translations['starting_download'])
        download_with_progress(CURSOR_DOWNLOAD_URL,
                               installer_path,
                               progress_callback,
                               translations)

        progress_callback(translations['download_complete'])
        subprocess.run([installer_path])

        progress_callback(translations['cleaning_files'])
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

        progress_callback(translations['install_complete'])
        return True

    except Exception as e:
        progress_callback(translations['error_occurred'].format(str(e)))
        return False


def block_cursor_updates():
    local_appdata = os.getenv('LOCALAPPDATA')
    if not local_appdata:
        return False
    updater_path = os.path.join(local_appdata, 'cursor-updater')

    try:
        if os.path.isdir(updater_path):
            shutil.rmtree(updater_path)
            open(updater_path, 'w').close()
        elif not os.path.exists(updater_path):
            open(updater_path, 'w').close()
        return True

    except Exception:
        pass

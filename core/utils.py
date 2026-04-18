#core/utils.py

import os
import sys
import re
import requests
import subprocess
import platform
import shutil
from pathlib import Path

def get_resource_path(relative_path):
    """Отримує шлях до ресурсів, адаптований для PyInstaller та звичайного запуску"""
    try:
        # Шлях для PyInstaller (_MEIPASS)
        base_path = sys._MEIPASS
    except Exception:
        # Звичайний шлях (корінь проекту)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)

def create_desktop_shortcut():
    """Створює або оновлює .desktop файли для Linux"""
    if platform.system() != "Linux":
        return

    project_root = Path(__file__).resolve().parent.parent
    main_py_path = project_root / "main.py"
    
    icon_path = get_resource_path("icons/main_icon.png")
    if not os.path.exists(icon_path):
        icon_path = get_resource_path("icons/mp4.png")
    
    desktop_file_content = f"""[Desktop Entry]
Name=UA Media Downloader
Exec=python3 {main_py_path}
Icon={icon_path}
Terminal=false
Type=Application
Categories=AudioVideo;Network;
Comment=Завантажувач медіа
Path={project_root}
StartupNotify=true
"""

    shortcuts = [
        Path.home() / "Desktop" / "UA Media Downloader.desktop",
        Path.home() / ".local" / "share" / "applications" / "ua_media_downloader.desktop"
    ]

    try:
        shortcuts[1].parent.mkdir(parents=True, exist_ok=True)
        for p in shortcuts:
            with open(p, "w") as f:
                f.write(desktop_file_content)
            os.chmod(p, 0o755)
        subprocess.run(["update-desktop-database", str(Path.home() / ".local/share/applications")], check=False)
        return True
    except Exception as e:
        print(f"Помилка оновлення ярлика: {e}")
        return False

def get_default_path():
    """Знаходить папку Музика/Відео через xdg-user-dir"""
    try:
        for xdg_type in ['MUSIC', 'VIDEOS']:
            path = subprocess.check_output(['xdg-user-dir', xdg_type], encoding='utf-8').strip()
            if path and os.path.exists(path):
                return path
    except:
        pass
    return os.path.join(os.path.expanduser("~"), "Videos")

def apply_system_fixes():
    """Фікси для X11/Wayland"""
    if platform.system() == "Linux":
        os.environ["QT_X11_NO_MITSHM"] = "1"

def check_ffmpeg():
    return shutil.which("ffmpeg")

def sniff_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': url
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        content = r.text
        
        # шукаємо прямі лінки
        found_links = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', content)
        
        # шукаємо iframe і шукаємо src у тегах iframe
        iframes = re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', content)
        
        for ifr_url in iframes:
            # відносні посилання в iframe
            if ifr_url.startswith('//'):
                ifr_url = 'https:' + ifr_url
            
            try:
                # всередину плеєра
                ifr_r = requests.get(ifr_url, headers={'Referer': url}, timeout=5)
                # пошук m3u8 всередині коду плеєра
                streams = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', ifr_r.text)
                found_links.extend(streams)
            except:
                continue

        # очистка
        final_links = [l.replace('\\/', '/') for l in found_links]
        return sorted(list(set(final_links)), reverse=True)

    except Exception as e:
        print(f"Deep sniff error: {e}")
        return []

    except Exception:
        return []
# core/utils.py 

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def create_desktop_shortcut():
    """Створює або оновлює .desktop файли, адаптуючись до переміщення папки."""
    if platform.system() != "Linux":
        return

    # КЛЮЧОВИЙ МОМЕНТ: Беремо шлях САМЕ ЗАРАЗ (там, де лежить запущений файл)
    project_root = Path(__file__).resolve().parent.parent
    main_py_path = project_root / "main.py"
    
    # Визначаємо іконку
    icon_path = project_root / "icons" / "main_icon.png"
    if not icon_path.exists():
        icon_path = project_root / "icons" / "mp4.png"
    
    # Генеруємо вміст із АКТУАЛЬНИМИ на цей момент шляхами
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

    # Шляхи до ярликів
    shortcuts = [
        Path.home() / "Desktop" / "UA Media Downloader.desktop",
        Path.home() / ".local" / "share" / "applications" / "ua_media_downloader.desktop"
    ]

    try:
        shortcuts[1].parent.mkdir(parents=True, exist_ok=True)
        
        for p in shortcuts:
            # Записуємо (або перезаписуємо) файл новими шляхами
            with open(p, "w") as f:
                f.write(desktop_file_content)
            os.chmod(p, 0o755)
            
        subprocess.run(["update-desktop-database", str(Path.home() / ".local/share/applications")], check=False)
        
        return True
    except Exception as e:
        print(f"Помилка оновлення ярлика: {e}")
        return False

def get_resource_path(relative_path):
    """Отримує шлях до ресурсів (іконок), адаптований для PyInstaller"""
    try:
        # Коли PyInstaller запустить програму, він створить папку _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Якщо ми просто запускаємо код (python main.py), беремо звичайний шлях
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def get_default_path():
    """Знаходить папку Відео/Музика незалежно від мови системи (XDG)"""
    try:
        # Пріоритет на папку MUSIC або VIDEOS
        path = subprocess.check_output(['xdg-user-dir', 'MUSIC'], encoding='utf-8').strip()
        if not path or not os.path.exists(path):
            path = subprocess.check_output(['xdg-user-dir', 'VIDEOS'], encoding='utf-8').strip()
        if path and os.path.exists(path):
            return path
    except:
        pass
    return os.path.join(os.path.expanduser("~"), "Videos")

def apply_system_fixes():
    """Фікси для стабільності GUI на Linux (Debian/Fedora)"""
    if platform.system() == "Linux":
        os.environ["QT_X11_NO_MITSHM"] = "1"
        # Можна додати специфічні змінні для відображення іконок

def check_ffmpeg():
    """Повертає шлях до ffmpeg або None"""
    return shutil.which("ffmpeg")

def get_resource_path(relative_path):
    """Отримує шлях до іконок та ресурсів"""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
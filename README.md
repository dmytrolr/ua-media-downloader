UA Media Downloader Pro 🚀

UA Media Downloader Pro — це потужний та інтуїтивно зрозумілий десктопний додаток на Python для завантаження медіаконтенту (відео та аудіо) з популярних веб-ресурсів. Побудований на базі yt-dlp та CustomTkinter, додаток поєднує в собі сучасний інтерфейс у стилі macOS та гнучкість професійних інструментів.
✨ Особливості

    🇺🇦 Повна підтримка української локалізації.

    🎥 Універсальність: завантаження відео (MP4 до 1080p+) та аудіо (MP3, FLAC, WAV, OGG).

    📋 Smart Paste: автоматичне підхоплення посилань із буфера обміну при фокусуванні на вікні.

    🔄 Черга завантажень: підтримка плейлистів та додавання кількох посилань одночасно.

    🛠 Debug Log: вбудоване вікно технічних деталей для моніторингу процесу в реальному часі.

    🐧 Native Linux Support: оптимізовано для роботи в середовищах Fedora (KDE Plasma) та Debian-based дистрибутивах (LMDE).

    📦 Portable & Installable: підтримка збірки в один файл (PyInstaller) та системні пакети (RPM).

🚀 Технології

    Language: Python 3.x

    UI Framework: CustomTkinter

    Core Engine: yt-dlp

    Backend Support: FFmpeg (для конвертації форматів)

    Packaging: PyInstaller & RPM Spec


🛠 Встановлення (для розробників)

    Клонуйте репозиторій:
    Bash

    git clone https://github.com/your-username/ua-media-downloader-pro.git
    cd ua-media-downloader-pro

    Встановіть залежності:
    Bash

    pip install -r requirements.txt

    Переконайтеся, що FFmpeg встановлено у вашій системі:

        Fedora: sudo dnf install ffmpeg

        Ubuntu/Debian/LMDE: sudo apt install ffmpeg

    Запуск:
    Bash

    python3 main.py
    
Плани

  Фіча	             Складність	                                    Що дасть користувачу
Smart Path	           Легка	         Автоматичне перемикання між папками «Музика» та «Відео» при зміні формату в меню.
File Manager Lite	 Середня	           Можливість навести лад у папках прямо з вікна вибору шляху (через filedialog).
Quality Selector	   Висока	            Якщо сніфер знайде декілька .m3u8 (наприклад, 480p та 1080p), дати користувачу вибрати потрібний.

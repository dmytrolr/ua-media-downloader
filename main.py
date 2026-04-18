import sys
import os
# Додаємо шлях до поточної директорії, щоб модулі core та gui завжди були доступні
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MediaDownloaderApp
from core.utils import apply_system_fixes
from core.utils import apply_system_fixes, create_desktop_shortcut # додай імпорт


# Ми визначаємо, де лежить бінарник
if getattr(sys, 'frozen', False):
    # Якщо програма зібрана PyInstaller-ом
    application_path = os.path.dirname(sys.executable)
else:
    # Якщо запускаєш просто скрипт
    application_path = os.path.dirname(os.path.abspath(__file__))

# Тепер створюємо абсолютний шлях до іконок
icons_path = os.path.join(application_path, 'icons')


# Приклад, як тепер завантажувати іконку:
# Замість path="icons/mp3.png" використовуй:
# path=os.path.join(icons_path, 'mp3.png')

def main():
    # Налаштування специфічних змінних оточення для Linux (LMDE/Fedora)
    apply_system_fixes()

    # Створюємо або оновлюємо ярлик при кожному запуску
    # Це гарантує, що якщо ти перенесеш папку, ярлик сам оновиться
    create_desktop_shortcut()
    
    # Передаємо шлях до іконок у конструктор класу
    app = MediaDownloaderApp(icons_path=icons_path)
    app.mainloop()

if __name__ == "__main__":
    main()
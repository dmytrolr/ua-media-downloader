# gui/main_window.py 
import os
import threading
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image
from core.utils import get_default_path, check_ffmpeg, sniff_url
from core.utils import sniff_url
from core.downloader import YtdlpCore
           
class MediaDownloaderApp(ctk.CTk):
    def __init__(self, icons_path=None): 
        super().__init__()

        if icons_path is None:
            self.icons_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons")
        else:
            self.icons_path = icons_path

        self.title("UA Media Downloader Pro")
        self.geometry("650x550")
        
        self.save_path = get_default_path()
        self.is_aborting = False
        self.show_logs = False
        self.last_pasted_url = ""  
                
        self.queue = []  
        self.is_processing = False  
        self.core = YtdlpCore(self)
        
        self.formats = {
            "MP3 (Стандарт)": ("mp3", "audio", "mp3.png"),
            "FLAC (Hi-Res)": ("flac", "audio", "flac.png"),
            "WAV (Lossless)": ("wav", "audio", "wav.png"),
            "OGG (Vorbis)": ("ogg", "audio", "ogg.png"),
            "MP4 (Відео 720p)": ("mp4", "video", "mp4.png"),
            "MP4 (Відео 1080p+)": ("mp4_best", "video", "mp4.png")
        }
        
        self.init_ui()
        self.setup_context_menu()
        self.check_dependencies()
        self.update_format_icon()
        self.bind("<FocusIn>", self.on_window_focus)
        

    def init_ui(self):
        self.bg_color, self.card_color = "#1E1E1E", "#2D2D2D"
        self.accent_color, self.text_dim = "#007AFF", "#A2A2A2"
        self.configure(fg_color=self.bg_color)

        self.log_view = ctk.CTkTextbox(self, width=600, height=0, font=("Courier New", 12), fg_color="#121212")
        self.log_view.pack(side="bottom", pady=(0, 10), padx=20, fill="x")

        self.log_btn = ctk.CTkButton(self, text="▼ Технічні деталі (debug)", fg_color="transparent", command=self.toggle_logs)
        self.log_btn.pack(side="bottom", pady=(5, 5))

        self.status_label = ctk.CTkLabel(self, text="Готово до роботи", text_color=self.text_dim)
        self.status_label.pack(side="bottom")

        self.progress_bar = ctk.CTkProgressBar(self, width=500, progress_color=self.accent_color)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="bottom", pady=5)
        self.progress_bar.pack_forget()

        self.main_frame = ctk.CTkFrame(self, corner_radius=20, fg_color=self.card_color, border_width=1, border_color="#3D3D3D")
        self.main_frame.pack(pady=20, padx=30, fill="both", expand=True)

        ctk.CTkLabel(self.main_frame, text="UA Media Downloader", font=("sans-serif", 24, "bold")).pack(pady=(25, 10))
        
        # Контейнер для поля вводу та кнопки сніфера
        self.url_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.url_container.pack(pady=10, padx=20, fill="x")

        self.url_entry = ctk.CTkEntry(
            self.url_container, 
            width=460, 
            height=45, 
            corner_radius=12, 
            placeholder_text="Вставте посилання..."
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.url_entry.bind("<Return>", lambda e: self.start_download_thread())

        # Кнопка сніфера 
        self.sniff_btn = ctk.CTkButton(
            self.url_container,
            text="Sniff", # Пишемо текстом, він точно відобразиться
            width=60,
            height=45,
            corner_radius=12,
            font=("sans-serif", 13, "bold"),
            fg_color="#3D3D3D",
            hover_color="#4D4D4D",
            command=self.start_sniffing
        )
        self.sniff_btn.pack(side="right", padx=(5, 0))

        self.settings_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.settings_frame.pack(pady=15, fill="x")

        self.format_combo = ctk.CTkComboBox(self.settings_frame, values=list(self.formats.keys()), command=self.update_format_icon, width=200)
        self.format_combo.set("MP3 (Стандарт)")
        self.format_combo.pack(side="left", padx=(100, 10))

        self.icon_label = ctk.CTkLabel(self.settings_frame, text="", width=48, height=48)
        self.icon_label.pack(side="left")

        self.path_btn = ctk.CTkButton(self.main_frame, text="📁 Обрати папку", command=self.choose_path, fg_color="#3D3D3D")
        self.path_btn.pack(pady=5)

        self.download_btn = ctk.CTkButton(self.main_frame, text="ЗАВАНТАЖИТИ", font=("sans-serif", 18, "bold"), height=55, fg_color=self.accent_color, command=self.start_download_thread)
        self.download_btn.pack(pady=(20, 25), padx=60, fill="x")

    def start_download_thread(self):
        if self.download_btn.cget("text") == "СКАСУВАТИ ВСЕ":
            self.is_aborting = True
            self.queue.clear()
            self.is_processing = False
            self.update_status("🛑 Скасовано", "red")
            self.download_btn.configure(state="normal", text="ЗАВАНТАЖИТИ")
            self.progress_bar.pack_forget()
            return

        raw_input = self.url_entry.get().strip()
        if not raw_input: return

        self.url_entry.delete(0, 'end')
        self.update_status("🔍 Аналізую...", "blue")
        self.is_aborting = False

        def fetch_logic():
            urls = [u for u in raw_input.split() if u.startswith("http")]
            if not urls: return
            
            for u in urls:
                extracted = self.core.extract_playlist_urls(u)
                for item in extracted:
                    self.queue.append(item)
                    title = item[1] if isinstance(item, tuple) else "Медіа"
                    self.after(0, lambda t=title: self.log(f"➕ В черзі: {t}"))
            
            if not self.is_processing and self.queue:
                self.after(0, self.process_queue)

        threading.Thread(target=fetch_logic, daemon=True).start()

    def process_queue(self):
        if not self.queue or self.is_aborting:
            self.is_processing = False
            if not self.is_aborting:
                self.update_status("✅ Всі завдання виконано", "green")
            self.download_btn.configure(text="ЗАВАНТАЖИТИ", state="normal")
            self.progress_bar.pack_forget()
            return

        self.is_processing = True
        self.download_btn.configure(text="СКАСУВАТИ ВСЕ")
        self.progress_bar.pack(side="bottom", pady=5)
        
        item = self.queue.pop(0)
        url, title = item if isinstance(item, tuple) else (item, "Медіа")
        
        # ОНОВЛЕННЯ СТАТУСУ
        self.update_status(f"📥 Завантаження: {title[:20]}...", self.accent_color)

        choice = self.format_combo.get()
        f_ext, m_type, _ = self.formats[choice]

        self.log(f"🚀 Початок: {title}")
        os.makedirs(self.save_path, exist_ok=True)

        threading.Thread(
            target=self.core.download_media,
            args=(url, self.save_path, f_ext, m_type),
            daemon=True
        ).start()

    def log(self, message):
        self.log_view.insert("end", f" {message}\n")
        self.log_view.see("end")

    def update_status(self, text, color=None):
        self.status_label.configure(text=text, text_color=color if color else self.text_dim)

    def choose_path(self):
        p = filedialog.askdirectory(initialdir=self.save_path)
        if p: self.save_path = p; self.log(f"📁 Шлях: {p}")

    def update_format_icon(self, choice=None):
        choice = self.format_combo.get()
        icon_name = self.formats[choice][2] 
        
        # Використовуємо переданий нам шлях до іконок
        full_icon_path = os.path.join(self.icons_path, icon_name)
        
        if os.path.exists(full_icon_path):
            try:
                img = Image.open(full_icon_path).convert("RGBA")
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(32, 32))
                self.icon_label.configure(image=ctk_img, text="")
            except Exception as e:
                self.log(f"❌ Помилка завантаження іконки: {e}")
        else:
            self.log(f"⚠️ Іконку не знайдено за шляхом: {full_icon_path}")
            self.icon_label.configure(image=None, text=icon_name[:3].upper())

    def setup_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Вставити", command=self.smart_paste)
        self.url_entry.bind("<Button-3>", lambda e: self.context_menu.post(e.x_root, e.y_root))

    def smart_paste(self):
        self.url_entry.delete(0, 'end')
        clip = self.clipboard_get().strip()
        self.url_entry.insert(0, clip)
        self.last_pasted_url = clip

    def toggle_logs(self):
        if not self.show_logs:
            self.geometry("650x850"); self.update_idletasks()
            self.log_view.configure(height=220); self.log_btn.configure(text="▲ Сховати деталі")
            self.show_logs = True
        else:
            self.log_view.configure(height=0); self.update_idletasks()
            self.geometry("650x550"); self.log_btn.configure(text="▼ Технічні деталі")
            self.show_logs = False

    def check_dependencies(self):
        if not check_ffmpeg(): self.update_status("⚠️ FFmpeg!", "red")

    def on_window_focus(self, event):
        try:
            clip = self.clipboard_get().strip()
            if clip.startswith("http") and not self.url_entry.get() and clip != self.last_pasted_url:
                self.url_entry.insert(0, clip)
                self.last_pasted_url = clip
                self.log("✨ Посилання підхоплено")
        except: pass

    def start_sniffing(self):
        url = self.url_entry.get().strip()
        if not url:
            self.log("⚠️ Вставте посилання для аналізу")
            return

        # кнопки
        self.sniff_btn.configure(state="disabled", text="⏳")
        self.update_status("🔍 Аналізую сторінку...", "#FFA500")
        
        self.log(f"🔎 Сніфер: аналіз сторінки {url}")
        
        def run():
            try:
                links = sniff_url(url)
                self.after(0, lambda: self.finish_sniffing(links))
            except Exception as e:
                self.after(0, lambda: self.log(f"❌ Помилка сніфера: {e}"))
                self.after(0, lambda: self.sniff_btn.configure(state="normal", text="🔍"))

        threading.Thread(target=run, daemon=True).start()

    def finish_sniffing(self, links):
        self.sniff_btn.configure(state="normal", text="Sniff") # Повертаємо текст
        
        if not links:
            # Один чіткий запис про невдачу
            self.log("❌ Сніфер не знайшов прямих посилань (сайт захищений)")
            self.update_status("Нічого не знайдено", "red")
            return

        # Якщо знайшли - показуємо лінк
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, links[0])
        self.log(f"✅ Знайдено потік: {links[0][:60]}...")
        self.update_status("Потік знайдено!", self.accent_color)
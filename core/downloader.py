# core/downloader.py 
import yt_dlp
import os

class YtdlpCore:
    def __init__(self, app_instance):
        self.app = app_instance 

    def extract_playlist_urls(self, url):
        """Розгортає плейлист у список кортежів (url, title)"""
        ydl_opts = {
            'extract_flat': True,
            'quiet': True,
            'nocheckcertificate': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and 'entries' in info:
                    urls = []
                    for entry in info['entries']:
                        if entry:
                            link = entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry['id']}"
                            title = entry.get('title', 'Unknown Title')
                            urls.append((link, title))
                    return urls
                return [(url, info.get('title', 'Video') if info else "Video")]
        except Exception as e:
            self.app.log(f"⚠️ Помилка аналізу: {e}")
            return [(url, "Video")]

    def download_media(self, url, download_path, format_ext, media_type):
        """Основний метод завантаження"""
        # Створюємо хук для прогрес-бару
        def progress_hook(d):
            if self.app.is_aborting:
                raise Exception("AbortByUser")
            if d['status'] == 'downloading':
                try:
                    p_raw = d.get('_percent_str', '0%')
                    p_float = float(p_raw.replace('%', '').strip()) / 100
                    self.app.after(0, lambda: self.app.progress_bar.set(p_float))
                    self.app.after(0, lambda: self.app.update_status(f"📥 Завантаження... {p_raw}"))
                except:
                    pass

        ydl_opts = self.get_ydl_opts(url, download_path, format_ext, media_type, progress_hook)

        try:
            # Важливо: використовуємо context manager для гарантії завершення
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Force download навіть якщо файл нібито є
                ydl.download([url])
            self.app.after(0, lambda: self.app.log(f"✅ Готово: {url[-12:]}"))
            self.app.after(0, lambda: self.app.update_status("✅ Файл збережено", "green"))
        except Exception as e:
            error_msg = str(e)
            if "AbortByUser" in error_msg:
                self.app.after(0, lambda: self.app.log("🛑 Скасовано користувачем."))
            else:
                # Виводимо ПОВНУ помилку для діагностики
                self.app.after(0, lambda: self.app.log(f"❌ Помилка завантаження: {error_msg[:100]}"))
                self.app.after(0, lambda: self.app.update_status("❌ Помилка завантаження", "red"))
        
        # Перехід до наступного в будь-якому випадку
        self.app.after(100, self.app.process_queue)

    def get_ydl_opts(self, url, download_path, format_ext, media_type, progress_hook):
        abs_path = os.path.abspath(download_path)
        
        ydl_opts = {
            'outtmpl': os.path.join(abs_path, '%(title)s.%(ext)s'),
            'noplaylist': True, 
            # Використовуємо новий формат словника
            'js_runtimes': {'node': {}}, 
            'logger': self.YtdlpLogger(self.app),
            'progress_hooks': [progress_hook],
            'writethumbnail': True,
            'quiet': True,
            'noprogress': True,
            'nocheckcertificate': True,
            'updatetime': False,
            'postprocessor_args': {
                'ffmpeg': ['-threads', '0'],
            },
        }
        
        if media_type == 'audio':
            audio_codec = 'vorbis' if format_ext == 'ogg' else format_ext
            bitrate = '320' if format_ext in ['mp3', 'ogg'] else None
            
            pps = [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': audio_codec, 'preferredquality': bitrate},
                {'key': 'FFmpegMetadata', 'add_metadata': True}
            ]
            if format_ext not in ['wav', 'pcm']:
                pps.append({'key': 'EmbedThumbnail'})
                
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': pps
            })
        else:
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',
                'postprocessors': [
                    {'key': 'FFmpegMetadata', 'add_metadata': True},
                    {'key': 'EmbedThumbnail'}
                ]
            })
        return ydl_opts

    class YtdlpLogger:
        def __init__(self, outer): self.outer = outer
        def debug(self, msg):
            if self.outer.is_aborting: raise Exception("AbortByUser")
        def warning(self, msg): pass
        def error(self, msg): self.outer.log(f"❌ {msg}")
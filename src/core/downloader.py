import os
import re
from PyQt6.QtCore import QThread, pyqtSignal
import yt_dlp
from yt_dlp import DownloadError


class VideoDownloader(QThread):
    progress_updated = pyqtSignal(int)
    log_updated = pyqtSignal(str)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    speed_updated = pyqtSignal(str)
    eta_updated = pyqtSignal(str)
    
    def __init__(self, url, quality, save_path):
        super().__init__()
        self.url = url
        self.quality = quality
        self.save_path = save_path
        self.ydl_opts = {}
        self._is_cancelled = False
    
    def cancel_download(self):
        """Método para cancelar la descarga"""
        self._is_cancelled = True
        self.log_updated.emit("Cancelando descarga...")
        self.terminate()  # Forzar terminación del hilo
        
    def run(self):
        try:
            if self._is_cancelled:
                return
                
            self.log_updated.emit(f"Iniciando descarga de: {self.url}")
            
            # Configurar opciones de yt-dlp según la calidad
            if self.quality == "Audio MP3":
                self.ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': os.path.join(self.save_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                    'js-runtimes': 'node',
                    'remote_components': ['ejs:github'],
                }
            else:
                # Configurar formato de video según calidad
                format_map = {
                    "1080p": "best[height<=1080][vcodec^=avc]",
                    "720p": "best[height<=720][vcodec^=avc]", 
                    "480p": "best[height<=480][vcodec^=avc]",
                    "360p": "best[height<=360][vcodec^=avc]"
                }
                
                selected_format = format_map.get(self.quality, "best[height<=720]")
                
                self.ydl_opts = {
                    'format': selected_format,
                    'outtmpl': os.path.join(self.save_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                    'js-runtimes': 'node',
                    'remote_components': ['ejs:github'],
                }
            
            # Extraer información del video primero
            with yt_dlp.YoutubeDL({'quiet': True, 'js-runtimes': 'node', 'remote_components': 'ejs:github'}) as ydl:
                info = ydl.extract_info(self.url, download=False)
                self.log_updated.emit(f"Título: {info.get('title', 'N/A')}")
                duration = info.get('duration', 0)
                self.log_updated.emit(f"Duración: {self.format_duration(duration)}")
            
            # Descargar el video
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([self.url])
            
            self.log_updated.emit("¡Descarga completada!")
            self.progress_updated.emit(100)
            self.finished.emit()
            
        except DownloadError as e:
            self.error_occurred.emit(f"Error de descarga: {str(e)}")
        except Exception as e:
            self.error_occurred.emit(f"Error inesperado: {str(e)}")
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            
            if total_bytes > 0:
                percent = int((downloaded_bytes / total_bytes) * 100)
                self.progress_updated.emit(percent)
                
                # Mostrar velocidad y ETA
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                
                if speed:
                    speed_str = f"{self.format_bytes(speed)}/s"
                    eta_str = self.format_eta(eta) if eta else "N/A"
                    self.speed_updated.emit(speed_str)
                    self.eta_updated.emit(eta_str)
                else:
                    self.speed_updated.emit("--")
                    self.eta_updated.emit("--")
                    
        elif d['status'] == 'finished':
            filename = d.get('filename', 'N/A')
            self.log_updated.emit(f"Descargado: {os.path.basename(filename)}")
            self.progress_updated.emit(100)
    
    def format_duration(self, seconds):
        if not seconds:
            return "N/A"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"
    
    def format_bytes(self, bytes_value):
        if bytes_value < 1024:
            return f"{bytes_value}B"
        elif bytes_value < 1024 * 1024:
            return f"{bytes_value/1024:.1f}KB"
        elif bytes_value < 1024 * 1024 * 1024:
            return f"{bytes_value/(1024*1024):.1f}MB"
        else:
            return f"{bytes_value/(1024*1024*1024):.1f}GB"
    
    def format_eta(self, seconds):
        """Formatear tiempo estimado en minutos y segundos"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = int(seconds % 60)
            return f"{minutes}m{remaining_seconds}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h{minutes}m"



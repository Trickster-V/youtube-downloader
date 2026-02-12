import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QProgressBar, QTextEdit,
                             QGroupBox, QGridLayout, QMessageBox, QFileDialog,
                             QListWidget, QListWidgetItem)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QIcon

from src.core.downloader import VideoDownloader
import yt_dlp
from yt_dlp import DownloadError


class PlaylistLoader(QThread):
    videos_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': False,
                'ignoreerrors': True,
                'js-runtimes': 'node',
                'remote_components': ['ejs:github'],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                
                if 'entries' in info:
                    videos = []
                    entries = info.get('entries', [])
                    
                    for i, entry in enumerate(entries):
                        if entry is None:
                            continue
                            
                        video_info = {
                            'index': i + 1,
                            'title': entry.get('title', 'Video sin título'),
                            'duration': entry.get('duration', 0),
                            'url': entry.get('webpage_url', entry.get('url', '')),
                            'id': entry.get('id', ''),
                            'uploader': entry.get('uploader', 'Desconocido'),
                        }
                        videos.append(video_info)
                    
                    self.videos_loaded.emit(videos)
                else:
                    self.error_occurred.emit("La URL no contiene una playlist válida")
                    
        except DownloadError as e:
            self.error_occurred.emit(f"Error al cargar playlist: {str(e)}")
        except Exception as e:
            self.error_occurred.emit(f"Error inesperado: {str(e)}")





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.setGeometry(100, 100, 900, 700)
        
        # Variables para descarga
        self.downloader_thread = None
        self.selected_videos = []
        self.videos = []
        self.is_playlist = False
        self.playlist_loader = None
        self.current_download_index = 0
        
        # Usar colores del sistema operativo
        self.setStyleSheet("")
        
        # Crear layout principal
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("📺 YouTube Downloader")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Grupo de URL
        url_group = QGroupBox("🔗 URL del Video/Lista")
        url_layout = QVBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("📋 Pega la URL de YouTube aquí...")
        self.url_input.textChanged.connect(self.on_url_changed)
        url_layout.addWidget(self.url_input)
        
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)
        
        # Grupo de opciones
        options_group = QGroupBox("⚙️ Opciones de Descarga")
        options_layout = QGridLayout()
        
        # Calidad
        options_layout.addWidget(QLabel("🎯 Calidad:"), 0, 0)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["1080p", "720p", "480p", "360p", "Audio MP3"])
        options_layout.addWidget(self.quality_combo, 0, 1)
        
        # Ruta de descarga
        options_layout.addWidget(QLabel("📁 Guardar en:"), 1, 0)
        self.path_label = QLabel(os.path.expanduser("~/Downloads"))
        options_layout.addWidget(self.path_label, 1, 1)
        
        self.browse_button = QPushButton("📂 Examinar")
        self.browse_button.clicked.connect(self.browse_folder)
        options_layout.addWidget(self.browse_button, 1, 2)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Grupo de selección de videos para playlists
        self.playlist_group = QGroupBox("📋 Videos de la Playlist")
        self.playlist_group.setVisible(False)
        playlist_layout = QVBoxLayout()
        
        # Controles de selección
        controls_layout = QHBoxLayout()
        
        self.selectAll_btn = QPushButton("✅ Seleccionar Todo")
        self.selectAll_btn.clicked.connect(self.select_all_videos)
        controls_layout.addWidget(self.selectAll_btn)
        
        self.deselectAll_btn = QPushButton("❌ Deseleccionar Todo")
        self.deselectAll_btn.clicked.connect(self.deselect_all_videos)
        controls_layout.addWidget(self.deselectAll_btn)
        
        controls_layout.addStretch()
        
        # Etiqueta de contador
        self.video_count_label = QLabel("0 videos seleccionados")
        self.video_count_label.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(self.video_count_label)
        
        playlist_layout.addLayout(controls_layout)
        
        # Lista de videos
        self.video_list = QListWidget()
        self.video_list.itemChanged.connect(self.on_video_item_changed)
        self.video_list.setMaximumHeight(200)
        playlist_layout.addWidget(self.video_list)
        
        self.playlist_group.setLayout(playlist_layout)
        layout.addWidget(self.playlist_group)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        self.download_button = QPushButton("⬇️ Descargar")
        self.download_button.clicked.connect(self.start_download)
        button_layout.addWidget(self.download_button)
        
        self.cancel_button = QPushButton("❌ Cancelar")
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setVisible(False)
        button_layout.addWidget(self.cancel_button)
        
        self.clear_button = QPushButton("🧹 Limpiar")
        self.clear_button.clicked.connect(self.clear_fields)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        # Barra de progreso con información de estado
        progress_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumWidth(400)
        progress_layout.addWidget(self.progress_bar)
        
        # Etiquetas de estado
        self.speed_label = QLabel("🚀 Velocidad: --")
        self.speed_label.setStyleSheet("QLabel { color: #666; font-size: 10px; min-width: 100px; }")
        self.speed_label.setVisible(False)
        progress_layout.addWidget(self.speed_label)
        
        self.eta_label = QLabel("⏱️ ETA: --")
        self.eta_label.setStyleSheet("QLabel { color: #666; font-size: 10px; min-width: 80px; }")
        self.eta_label.setVisible(False)
        progress_layout.addWidget(self.eta_label)
        
        progress_layout.addStretch()
        layout.addLayout(progress_layout)
        
        # Área de log
        log_group = QGroupBox("📋 Registro de Actividad")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "📂 Seleccionar carpeta de descarga")
        if folder:
            self.path_label.setText(folder)
            
    def log_message(self, message):
        self.log_text.append(message)
        
    def clear_fields(self):
        self.url_input.clear()
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.speed_label.setText("🚀 Velocidad: --")
        self.eta_label.setText("⏱️ ETA: --")
        self.selected_videos = []
        self.videos = []
        self.video_list.clear()
        self.playlist_group.setVisible(False)
        self.current_download_index = 0
        
    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Por favor ingresa una URL válida")
            return
            
        quality = self.quality_combo.currentText()
        save_path = self.path_label.text()
        
        # Verificar si es una playlist y hay videos seleccionados
        if self.is_playlist and self.videos:
            # Obtener videos seleccionados
            self.selected_videos = []
            for i in range(self.video_list.count()):
                item = self.video_list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    video = item.data(Qt.ItemDataRole.UserRole)
                    self.selected_videos.append(video)
            
            if not self.selected_videos:
                QMessageBox.warning(self, "Error", "Por favor selecciona al menos un video para descargar")
                return
            
            # Iniciar descarga secuencial de múltiples videos
            self.current_download_index = 0
            self.download_next_video(quality, save_path)
        else:
            # Descarga directa de video individual
            self.log_message(f"🎬 Descargando video individual...")
            self.downloader_thread = VideoDownloader(url, quality, save_path)
            self.start_download_thread()
    
    def download_next_video(self, quality, save_path):
        """Descargar el siguiente video de la lista"""
        if self.current_download_index >= len(self.selected_videos):
            # Todos los videos han sido descargados
            self.log_message(f"✅ ¡Descarga completada! {len(self.selected_videos)} videos descargados")
            self.download_finished()
            return
        
        video = self.selected_videos[self.current_download_index]
        self.log_message(f"📹 Descargando video {self.current_download_index + 1}/{len(self.selected_videos)}: {video['title']}")
        
        self.downloader_thread = VideoDownloader(video['url'], quality, save_path)
        self.start_download_thread()
    
    
    
    def start_download_thread(self):
        """Iniciar el hilo de descarga"""
        self.downloader_thread.progress_updated.connect(self.update_progress)
        self.downloader_thread.log_updated.connect(self.log_message)
        self.downloader_thread.finished.connect(self.on_video_finished)
        self.downloader_thread.error_occurred.connect(self.on_video_error)
        self.downloader_thread.speed_updated.connect(self.update_speed)
        self.downloader_thread.eta_updated.connect(self.update_eta)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.speed_label.setVisible(True)
        self.eta_label.setVisible(True)
        self.speed_label.setText("🚀 Velocidad: --")
        self.eta_label.setText("⏱️ ETA: --")
        self.download_button.setVisible(False)
        self.cancel_button.setVisible(True)
        self.downloader_thread.start()
    
    def on_video_finished(self):
        """Manejar la finalización de un video individual"""
        self.current_download_index += 1
        
        if self.is_playlist and self.selected_videos:
            # Continuar con el siguiente video si hay más
            quality = self.quality_combo.currentText()
            save_path = self.path_label.text()
            self.download_next_video(quality, save_path)
        else:
            # Video individual finalizado
            self.download_finished()
    
    def on_video_error(self, error_msg):
        """Manejar error en la descarga de un video"""
        if self.is_playlist and self.selected_videos:
            # Para playlist, continuar con el siguiente video a pesar del error
            video = self.selected_videos[self.current_download_index]
            self.log_message(f"❌ Error en '{video['title']}': {error_msg}")
            self.current_download_index += 1
            
            quality = self.quality_combo.currentText()
            save_path = self.path_label.text()
            self.download_next_video(quality, save_path)
        else:
            # Error en video individual
            self.download_error(error_msg)
    
    def cancel_download(self):
        """Método para cancelar la descarga actual"""
        if self.downloader_thread and self.downloader_thread.isRunning():
            reply = QMessageBox.question(
                self, 
                "Cancelar Descarga", 
                "¿Estás seguro de que deseas cancelar la descarga actual?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Llamar al método de cancelación del downloader
                self.downloader_thread.cancel_download()
                
                # Esperar a que el hilo termine
                self.downloader_thread.wait(3000)  # Esperar máximo 3 segundos
                
                # Restablecer interfaz
                self.log_message("Descarga cancelada por el usuario")
                self.progress_bar.setVisible(False)
                self.speed_label.setVisible(False)
                self.eta_label.setVisible(False)
                self.download_button.setVisible(True)
                self.download_button.setEnabled(True)
                self.cancel_button.setVisible(False)
        
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def update_speed(self, speed_text):
        self.speed_label.setText(f"🚀 Velocidad: {speed_text}")
    
    def update_eta(self, eta_text):
        self.eta_label.setText(f"⏱️ ETA: {eta_text}")
        
    def download_finished(self):
        """Manejar finalización completa de todas las descargas"""
        self.progress_bar.setValue(100)
        self.speed_label.setVisible(False)
        self.eta_label.setVisible(False)
        self.download_button.setVisible(True)
        self.download_button.setEnabled(True)
        self.cancel_button.setVisible(False)
        
        if not (self.is_playlist and self.selected_videos):
            # Solo mostrar mensaje para video individual
            self.log_message("✅ ¡Descarga completada!")
        
    def on_url_changed(self):
        """Detectar si es una playlist y cargar videos"""
        url = self.url_input.text().strip()
        
        # Limpiar si cambia la URL
        if url != getattr(self, '_last_url', ''):
            self.videos = []
            self.video_list.clear()
            self.playlist_group.setVisible(False)
            self.is_playlist = False
            self._last_url = url
        
        # Detectar si es una playlist
        if url and 'playlist' in url.lower():
            self.start_playlist_loader(url)
    
    def start_playlist_loader(self, url):
        """Iniciar carga de playlist en segundo plano"""
        self.log_message("🔍 Analizando playlist...")
        
        # Cancelar loader anterior si existe
        if self.playlist_loader and self.playlist_loader.isRunning():
            self.playlist_loader.terminate()
            self.playlist_loader.wait()
        
        self.playlist_loader = PlaylistLoader(url)
        self.playlist_loader.videos_loaded.connect(self.on_playlist_loaded)
        self.playlist_loader.error_occurred.connect(self.on_playlist_error)
        self.playlist_loader.start()
    
    def on_playlist_loaded(self, videos):
        """Manejar videos cargados de la playlist"""
        self.is_playlist = True
        self.videos = []
        
        for video in videos:
            video['duration'] = self.format_duration(video['duration'])
            self.videos.append(video)
        
        self.populate_video_list()
        self.log_message(f"✅ Playlist detectada: {len(self.videos)} videos")
    
    def on_playlist_error(self, error_msg):
        """Manejar error al cargar playlist"""
        self.log_message(f"❌ {error_msg}")
        self.is_playlist = False
    
    def populate_video_list(self):
        """Llenar la lista de videos"""
        self.video_list.clear()
        
        for video in self.videos:
            item = QListWidgetItem()
            item.setText(f"📹 {video['index']:3d}. {video['title'][:60]}... ({video['duration']})")
            item.setData(Qt.ItemDataRole.UserRole, video)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            
            self.video_list.addItem(item)
        
        # Mostrar grupo de playlist
        self.playlist_group.setVisible(True)
        self.update_video_count()
    
    def select_all_videos(self):
        """Seleccionar todos los videos"""
        for i in range(self.video_list.count()):
            item = self.video_list.item(i)
            item.setCheckState(Qt.CheckState.Checked)
        self.update_video_count()
    
    def deselect_all_videos(self):
        """Deseleccionar todos los videos"""
        for i in range(self.video_list.count()):
            item = self.video_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)
        self.update_video_count()
    
    def on_video_item_changed(self, item):
        """Actualizar contador cuando cambia la selección"""
        self.update_video_count()
    
    def update_video_count(self):
        """Actualizar contador de videos seleccionados"""
        checked_count = 0
        for i in range(self.video_list.count()):
            item = self.video_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                checked_count += 1
        
        self.video_count_label.setText(f"{checked_count} videos seleccionados")
    
    def format_duration(self, seconds):
        """Formatear duración del video"""
        if not seconds:
            return "N/A"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"
    
    def download_error(self, error_msg):
        QMessageBox.critical(self, "Error de Descarga", error_msg)
        self.download_button.setVisible(True)
        self.download_button.setEnabled(True)
        self.cancel_button.setVisible(False)
        self.progress_bar.setVisible(False)
        self.speed_label.setVisible(False)
        self.eta_label.setVisible(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
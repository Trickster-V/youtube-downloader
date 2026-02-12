# 🎬 YouTube Downloader

Una aplicación de escritorio desarrollada con Python y PyQt6 para descargar videos y listas de reproducción de YouTube con una interfaz moderna y amigable.

## ✨ Características

- 🎥 Descargar videos individuales de YouTube
- 📋 Descargar listas de reproducción completas con selección personalizada
- 🎯 Selección de calidad (1080p, 720p, 480p, 360p)
- 🎵 Extracción y descarga de audio en formato MP3
- 🖥️ Interfaz gráfica moderna con PyQt6
- 📊 Barra de progreso en tiempo real
- 📝 Registro de actividad detallado
- ⚡ Monitorización de velocidad de descarga
- ⏱️ Tiempo estimado de finalización (ETA)
- ✅ Selección individual de videos en playlists
- 🚀 Descargas secuenciales para playlists
- ❌ Cancelación de descargas en curso
- 🧹 Función de limpiar campos
- 📂 Selector de carpetas de destino
- 🔍 Detección automática de playlists
- 🔄 Conversión automática de formatos
- 🎬 Soporte para múltiples codecs de video

## 📁 Estructura del Proyecto

```
youtube_downloader/
├── main.py                 # Punto de entrada principal
├── requirements.txt        # Dependencias del proyecto
├── src/
│   ├── core/
│   │   └── downloader.py   # Lógica de descarga con yt-dlp
│   └── ui/
│       └── main_window.py  # Interfaz gráfica con PyQt6
└── README.md              # Documentación del proyecto
```

## 🚀 Instalación

### Requisitos previos
- Python 3.8 o superior
- FFmpeg (necesario para conversiones de audio)

1. 📥 Clonar o descargar este repositorio:
   ```bash
   git clone <repository-url>
   cd youtube_downloader
   ```

2. 📦 Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. 🔧 Instalar FFmpeg si no lo tienes:
   - **Windows:** Descargar desde [ffmpeg.org](https://ffmpeg.org/download.html) y agregar al PATH
   - **macOS:** `brew install ffmpeg`
   - **Linux:** `sudo apt install ffmpeg`

## 🎮 Uso

1. ▶️ Ejecutar la aplicación:
   ```bash
   python main.py
   ```

2. 🔗 Pega la URL del video o playlist de YouTube en el campo correspondiente

3. 🎯 **Para videos individuales:**
   - Selecciona la calidad deseada (1080p, 720p, 480p, 360p o Audio MP3)
   - Elige la carpeta de destino
   - Haz clic en "Descargar"

4. 📋 **Para playlists:**
   - La aplicación detectará automáticamente la playlist
   - Se mostrará una lista con todos los videos
   - Selecciona los videos que deseas descargar (todos por defecto)
   - Configura calidad y destino
   - Haz clic en "Descargar"

5. 📊 **Durante la descarga:**
   - Monitoriza el progreso en tiempo real
   - Visualiza la velocidad de descarga y tiempo restante
   - Consulta el registro de actividad para detalles
   - Puedes cancelar la descarga si es necesario

## 📚 Dependencias

Las dependencias principales se definen en `requirements.txt`:

- 🐍 **PyQt6 >= 6.5.0** - Framework para la interfaz gráfica
- 📺 **yt-dlp >= 2023.12.30** - Motor principal para descargas de YouTube
- 🌐 **requests >= 2.31.0** - Manejo de solicitudes HTTP

## ⚙️ Características Técnicas

### Arquitectura
- **Patrón MVC**: Separación clara entre UI y lógica de negocio
- **Multithreading**: Descargas en hilos separados para no bloquear la UI
- **Manejo de errores**: Robusta gestión de excepciones y reintentos
- **Señales y slots**: Comunicación eficiente entre componentes PyQt6

### Formatos Soportados
- **Video**: MP4 (H.264/AVC) en múltiples resoluciones (1080p, 720p, 480p, 360p)
- **Audio**: MP3 con calidad de 192 kbps
- **Playlist**: Procesamiento automático y descarga selectiva

### Optimizaciones
- 🔍 Detección automática de playlists mediante análisis de URL
- 🚀 Descargas secuenciales para evitar sobrecarga del servidor
- 🔄 Conversión de audio con FFmpeg integrado
- 💾 Sistema de caché para metadatos de videos
- 📈 Formateo inteligente de velocidades y tiempos

### Componentes Principales

#### VideoDownloader (src/core/downloader.py)
- 🧵 Hilo separado para descargas no bloqueantes
- ⚙️ Configuración dinámica según calidad seleccionada
- 📊 Hooks de progreso con actualización en tiempo real
- 📏 Formateo de bytes, duración y ETA
- 🛑 Manejo de cancelación de descargas

#### MainWindow (src/ui/main_window.py)
- 🖥️ Interfaz completa con PyQt6
- 🔍 Detección automática de playlists
- ✅ Gestión de selección de videos
- 📊 Monitorización de múltiples descargas secuenciales
- 📝 Sistema de logs integrado

#### Configuración yt-dlp
- ⚡ Runtimes de JavaScript para bypass de restricciones
- 🌐 Componentes remotos para máxima compatibilidad
- 📝 Templates de salida personalizables
- 🎵 Post-procesamiento para audio

## 🛠️ Desarrollo

### Ejecución en modo desarrollo
```bash
python src/ui/main_window.py  # Solo interfaz
python src/core/downloader.py # Solo motor (requiere parámetros)
```

### Personalización
- 🎨 La interfaz permite fácil personalización de estilos y colores
- ⚙️ El motor de descarga soporta formatos adicionales mediante configuración
- 📝 Sistema de logs extensible para debugging
- 🏗️ Arquitectura modular para agregar nuevas funcionalidades
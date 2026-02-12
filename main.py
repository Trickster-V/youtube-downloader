#!/usr/bin/env python3
"""
YouTube Downloader - Aplicación para descargar videos y listas de YouTube
Autor: OpenCode
"""

import sys
import os

# Agregar el directorio src al path para poder importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication


def main():
    """Función principal para ejecutar la aplicación"""
    app = QApplication(sys.argv)
    
    # Configurar aplicación
    app.setApplicationName("YouTube Downloader")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("OpenCode")
    
    # Crear y mostrar ventana principal
    window = MainWindow()
    window.show()
    
    # Ejecutar bucle de eventos
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
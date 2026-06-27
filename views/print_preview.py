from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
import qtawesome as qta
import os

class PrintPreviewDialog(QDialog):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        from utils.translation_manager import tr, tr_manager
        self.setWindowTitle(tr("document_preview"))
        self.resize(1000, 800)
        self.file_path = file_path
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Internal PDF Viewer using WebEngine (Chromium-based)
        self.web_view = QWebEngineView()
        # Optimization: Clear cache on each load for freshness
        self.web_view.page().profile().clearHttpCache()
        # Set settings to allow local file access
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PluginsEnabled, True)

        # Convert path to URL
        from PySide6.QtCore import QUrl
        file_url = QUrl.fromLocalFile(os.path.abspath(self.file_path))
        self.web_view.load(file_url)

        layout.addWidget(self.web_view)

        btn_layout = QHBoxLayout()
        from utils.translation_manager import tr

        external_btn = QPushButton(tr("open_externally"))
        external_btn.setIcon(qta.icon("fa5s.external-link-alt"))
        external_btn.clicked.connect(self.open_file)

        close_btn = QPushButton(tr("close"))
        close_btn.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(external_btn)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def open_file(self):
        import subprocess, platform
        try:
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', self.file_path))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(self.file_path)
            else:                                   # linux variants
                subprocess.call(('xdg-open', self.file_path))
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "خطأ", f"فشل فتح الملف: {str(e)}")

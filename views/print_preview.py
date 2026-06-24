from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt
import qtawesome as qta
import os

class PrintPreviewDialog(QDialog):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("معاينة المستند")
        self.resize(800, 600)
        self.file_path = file_path
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        info_label = QLabel(f"تم توليد المستند بنجاح:\n{os.path.abspath(self.file_path)}")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 14px; margin: 20px;")
        layout.addWidget(info_label)

        icon_label = QLabel()
        icon_label.setPixmap(qta.icon("fa5s.file-pdf", color="#e74c3c").pixmap(100, 100))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        btn_layout = QHBoxLayout()
        open_btn = QPushButton("فتح الملف")
        open_btn.setObjectName("GoldButton")
        open_btn.clicked.connect(self.open_file)

        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(open_btn)
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()

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

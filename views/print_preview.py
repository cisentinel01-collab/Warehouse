from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QFrame, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt
import os
import sys

class PrintPreviewDialog(QDialog):
    def __init__(self, pdf_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("معاينة الفاتورة")
        self.resize(800, 600)
        self.pdf_path = os.path.abspath(pdf_path)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header info
        header = QFrame()
        header.setStyleSheet("background-color: #1a2a6c; border-radius: 8px;")
        h_layout = QHBoxLayout(header)
        title = QLabel("تم توليد الملف بنجاح")
        title.setStyleSheet("color: #d4af37; font-size: 18px; font-weight: bold; padding: 10px;")
        h_layout.addWidget(title)
        layout.addWidget(header)

        # File path display
        path_frame = QFrame()
        path_frame.setObjectName("Card")
        p_layout = QVBoxLayout(path_frame)
        p_layout.addWidget(QLabel("مسار الملف:"))
        path_label = QLabel(self.pdf_path)
        path_label.setWordWrap(True)
        path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        path_label.setStyleSheet("color: #ffffff; font-family: 'Courier New'; font-weight: bold; border: 1px solid #dcdde1; padding: 10px; background: #111111;")
        p_layout.addWidget(path_label)
        layout.addWidget(path_frame)

        info_label = QLabel("يمكنك فتح الملف للمعاينة أو إرساله للطباعة مباشرة.")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        layout.addStretch()

        # Action Buttons
        btn_layout = QHBoxLayout()

        open_btn = QPushButton("فتح والمعاينة")
        open_btn.setObjectName("GoldButton")
        open_btn.setMinimumHeight(50)
        open_btn.clicked.connect(self.open_file)
        btn_layout.addWidget(open_btn)

        print_btn = QPushButton("طباعة")
        print_btn.setObjectName("PrimaryButton")
        print_btn.setMinimumHeight(50)
        print_btn.clicked.connect(self.print_file)
        btn_layout.addWidget(print_btn)

        close_btn = QPushButton("إغلاق")
        close_btn.setMinimumHeight(50)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def open_file(self):
        try:
            if sys.platform == 'win32':
                os.startfile(self.pdf_path)
            elif sys.platform == 'darwin':
                os.system(f'open "{self.pdf_path}"')
            else:
                os.system(f'xdg-open "{self.pdf_path}"')
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل فتح الملف: {str(e)}")

    def print_file(self):
        try:
            if sys.platform == 'win32':
                import win32api
                import win32print
                win32api.ShellExecute(0, "print", self.pdf_path, None, ".", 0)
            else:
                os.system(f'lp "{self.pdf_path}"')
            QMessageBox.information(self, "طباعة", "تم إرسال الأمر للطابعة")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل الطباعة: {str(e)}")

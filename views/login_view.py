from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QLabel, QMessageBox)
from PySide6.QtCore import Qt
import qtawesome as qta
from utils.auth import AuthManager

class LoginView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تسجيل الدخول - AMS WMS")
        self.setFixedSize(400, 500)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Logo/Icon
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon("fa5s.warehouse", color="#1a2a6c").pixmap(80, 80))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        title = QLabel("تسجيل الدخول للنظام")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a2a6c;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.username = QLineEdit()
        self.username.setPlaceholderText("اسم المستخدم")
        self.username.setMinimumHeight(45)
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("كلمة المرور")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setMinimumHeight(45)
        layout.addWidget(self.password)

        login_btn = QPushButton("دخول")
        login_btn.setObjectName("PrimaryButton")
        login_btn.setMinimumHeight(50)
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)

        layout.addStretch()

        footer = QLabel("American Marine Services")
        footer.setStyleSheet("color: grey; font-size: 10px;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

    def handle_login(self):
        user = self.username.text()
        pw = self.password.text()

        if AuthManager.login(user, pw):
            from views.main_window import MainWindow
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة")

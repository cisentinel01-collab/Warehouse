import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from views.login_view import LoginView
from database.migrate import migrate
from utils.device_manager import register_device, check_device_status


def main():
    # إنشاء المجلدات المطلوبة
    for d in ["reports", "backups", "images/barcodes", "logo"]:
        os.makedirs(d, exist_ok=True)

    # تشغيل الـ Migration
    try:
        migrate()
    except Exception as e:
        print(f"Migration error: {e}")

    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)

    # تحميل الـ Style
    try:
        with open("assets/styles.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Style loading error: {e}")

    # تسجيل الجهاز إذا لم يكن موجودًا
    try:
        register_device()

        allowed, message = check_device_status()

        if not allowed:
            QMessageBox.critical(
                None,
                "Device Access",
                message
            )
            sys.exit()

    except Exception as e:
        QMessageBox.critical(
            None,
            "Device Error",
            str(e)
        )
        sys.exit()

    # فتح شاشة تسجيل الدخول
    login = LoginView()
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
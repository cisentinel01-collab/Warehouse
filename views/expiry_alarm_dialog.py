from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QScrollArea, QWidget, QFrame
from PySide6.QtCore import Qt, QUrl
# Optional audio import
try:
    from PySide6.QtMultimedia import QSoundEffect
except ImportError:
    QSoundEffect = None

import qtawesome as qta

class ExpiryAlarmDialog(QDialog):
    def __init__(self, expired_batches, expiring_soon, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تنبيه انتهاء الصلاحية")
        self.resize(600, 500)
        self.setStyleSheet("background-color: #1a1a1a; color: white;")

        self.sound = None
        if QSoundEffect:
            try:
                self.sound = QSoundEffect(self)
                # Using a system beep or a common sound path if available
                # self.sound.setSource(QUrl.fromLocalFile("assets/alarm.wav"))
                self.sound.setLoopCount(QSoundEffect.Infinite)
                # self.sound.play() # Start playing
            except: pass

        layout = QVBoxLayout(self)

        header = QLabel("تنبيه: يوجد أصناف منتهية أو قاربت على الانتهاء")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #e74c3c; padding: 10px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: #000000; border: none;")
        content = QWidget()
        c_layout = QVBoxLayout(content)

        # Expired
        if expired_batches:
            exp_label = QLabel("أصناف منتهية الصلاحية:")
            exp_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14px;")
            c_layout.addWidget(exp_label)
            for b in expired_batches:
                frame = QFrame()
                frame.setStyleSheet("border: 1px solid #e74c3c; border-radius: 5px; padding: 5px; background: #2c0000;")
                f_layout = QVBoxLayout(frame)
                f_layout.addWidget(QLabel(f"الصنف: {b['item_name']} ({b['item_code']})"))
                f_layout.addWidget(QLabel(f"رقم التشغيلة: {b['batch_number']} | الكمية: {b['quantity']}"))
                f_layout.addWidget(QLabel(f"تاريخ الانتهاء: {b['expiry_date']}"))
                c_layout.addWidget(frame)

        # Expiring Soon
        if expiring_soon:
            soon_label = QLabel("أصناف تنتهي خلال 6 أشهر:")
            soon_label.setStyleSheet("color: #f1c40f; font-weight: bold; font-size: 14px; margin-top: 10px;")
            c_layout.addWidget(soon_label)
            for b in expiring_soon:
                frame = QFrame()
                frame.setStyleSheet("border: 1px solid #f1c40f; border-radius: 5px; padding: 5px; background: #2c2c00;")
                f_layout = QVBoxLayout(frame)
                f_layout.addWidget(QLabel(f"الصنف: {b['item_name']} ({b['item_code']})"))
                f_layout.addWidget(QLabel(f"رقم التشغيلة: {b['batch_number']} | الكمية: {b['quantity']}"))
                f_layout.addWidget(QLabel(f"تاريخ الانتهاء: {b['expiry_date']}"))
                c_layout.addWidget(frame)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        self.stop_btn = QPushButton("إيقاف التنبيه")
        self.stop_btn.setObjectName("GoldButton")
        self.stop_btn.setFixedHeight(50)
        self.stop_btn.clicked.connect(self.stop_alarm)
        layout.addWidget(self.stop_btn)

    def stop_alarm(self):
        if self.sound:
            self.sound.stop()
        self.accept()

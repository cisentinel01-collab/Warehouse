from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QLabel, QHeaderView, QGroupBox, QFormLayout,
                             QMessageBox, QTabWidget, QSpinBox)
from PySide6.QtCore import Qt
from models.inventory import Settings

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        self.model = Settings()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Company Info Tab
        self.company_tab = QWidget()
        self.setup_company_tab()
        self.tabs.addTab(self.company_tab, "بيانات الشركة")

        # Notification Settings Tab
        self.notify_tab = QWidget()
        self.setup_notify_tab()
        self.tabs.addTab(self.notify_tab, "إعدادات التنبيهات")

    def setup_company_tab(self):
        layout = QVBoxLayout(self.company_tab)
        group = QGroupBox("إعدادات عامة")
        form = QFormLayout(group)

        settings = self.model.get_settings()

        self.name_input = QLineEdit(settings.get('company_name', ''))
        self.addr_input = QLineEdit(settings.get('address', ''))
        self.phone_input = QLineEdit(settings.get('phone', ''))
        self.email_input = QLineEdit(settings.get('email', ''))

        form.addRow("اسم الشركة:", self.name_input)
        form.addRow("العنوان:", self.addr_input)
        form.addRow("الهاتف:", self.phone_input)
        form.addRow("البريد الإلكتروني:", self.email_input)

        save_btn = QPushButton("حفظ الإعدادات")
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self.save_company_settings)
        form.addRow(save_btn)

        layout.addWidget(group)
        layout.addStretch()

    def setup_notify_tab(self):
        layout = QVBoxLayout(self.notify_tab)
        group = QGroupBox("تنبيهات المخزون")
        form = QFormLayout(group)

        self.low_stock_limit = QSpinBox()
        self.low_stock_limit.setRange(1, 1000)
        self.low_stock_limit.setSuffix(" قطعة")
        self.low_stock_limit.setValue(10) # Default

        form.addRow("تنبيه عند وصول المخزون لـ:", self.low_stock_limit)

        save_btn = QPushButton("حفظ إعدادات التنبيه")
        save_btn.setObjectName("GoldButton")
        save_btn.clicked.connect(lambda: QMessageBox.information(self, "نجاح", "تم حفظ إعدادات التنبيهات"))
        form.addRow(save_btn)

        layout.addWidget(group)
        layout.addStretch()

    def save_company_settings(self):
        data = {
            "company_name": self.name_input.text(),
            "address": self.addr_input.text(),
            "phone": self.phone_input.text(),
            "email": self.email_input.text()
        }
        self.model.update_settings(data)
        QMessageBox.information(self, "نجاح", "تم حفظ الإعدادات بنجاح")

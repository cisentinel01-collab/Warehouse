from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                             QHeaderView, QComboBox, QMessageBox)
from PySide6.QtCore import Qt
import qtawesome as qta
from models.inventory import Location

class LocationsView(QWidget):
    def __init__(self):
        super().__init__()
        self.model = Location()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Toolbar
        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("بحث عن موقع...")
        self.search_input.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search_input)

        add_btn = QPushButton("إضافة موقع جديد")
        add_btn.setObjectName("PrimaryButton")
        add_btn.setIcon(qta.icon("fa5s.plus", color="white"))
        add_btn.clicked.connect(self.show_add_dialog)
        toolbar.addWidget(add_btn)

        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["المعرف", "اسم الموقع", "الوصف", "إجراءات"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self):
        term = self.search_input.text()
        if term:
            locations = self.model.execute_query("SELECT * FROM locations WHERE name LIKE %s AND is_deleted = 0", (f"%{term}%",))
        else:
            locations = self.model.get_all()

        self.table.setRowCount(0)
        for loc in locations:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(loc['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(str(loc['name'])))
            self.table.setItem(row, 2, QTableWidgetItem(str(loc['description'] or "")))

            del_btn = QPushButton()
            del_btn.setIcon(qta.icon("fa5s.trash-alt", color="white"))
            del_btn.setFixedSize(30, 30)
            del_btn.setStyleSheet("background-color: #e74c3c; border-radius: 5px;")
            del_btn.clicked.connect(lambda _, l=loc: self.handle_delete(l))
            self.table.setCellWidget(row, 3, del_btn)

    def handle_delete(self, loc):
        if QMessageBox.question(self, "تأكيد", f"حذف الموقع '{loc['name']}'؟") == QMessageBox.Yes:
            self.model.update(loc['id'], {"is_deleted": 1})
            self.refresh()

    def show_add_dialog(self):
        from PySide6.QtWidgets import QDialog, QFormLayout
        dialog = QDialog(self)
        dialog.setWindowTitle("إضافة موقع جديد")
        d_layout = QFormLayout(dialog)

        name_input = QLineEdit()
        desc_input = QLineEdit()

        d_layout.addRow("اسم الموقع:", name_input)
        d_layout.addRow("الوصف:", desc_input)

        save_btn = QPushButton("حفظ")
        save_btn.setObjectName("GoldButton")
        save_btn.clicked.connect(lambda: self.save_location(dialog, name_input.text(), desc_input.text()))
        d_layout.addRow(save_btn)

        dialog.exec()

    def save_location(self, dialog, name, desc):
        if not name:
            QMessageBox.warning(self, "تنبيه", "الاسم مطلوب")
            return

        self.model.create({"name": name, "description": desc})
        dialog.accept()
        self.refresh()

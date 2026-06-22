from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                             QHeaderView, QGroupBox, QMessageBox)
from PySide6.QtCore import Qt
import qtawesome as qta

class SuppliersView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Toolbar
        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("بحث عن مورد...")
        self.search_input.textChanged.connect(self.handle_search)
        toolbar.addWidget(self.search_input)

        add_btn = QPushButton("إضافة مورد")
        add_btn.setObjectName("PrimaryButton")
        add_btn.setIcon(qta.icon("fa5s.plus", color="white"))
        from utils.auth import AuthManager
        if not AuthManager.has_permission('suppliers', 'add'):
            add_btn.setEnabled(False)

        add_btn.clicked.connect(self.show_add_dialog)
        toolbar.addWidget(add_btn)

        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["الاسم", "الهاتف", "البريد", "العنوان", "ملاحظات", "إجراءات"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch) # Name stretches
        self.table.horizontalHeader().setDefaultSectionSize(130)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self, suppliers=None):
        if suppliers is None:
            suppliers = self.controller.get_all_suppliers()

        self.table.setRowCount(0)
        for s in suppliers:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(s['name'])))
            self.table.setItem(row, 1, QTableWidgetItem(str(s['phone'] or "")))
            self.table.setItem(row, 2, QTableWidgetItem(str(s['email'] or "")))
            self.table.setItem(row, 3, QTableWidgetItem(str(s['address'] or "")))
            self.table.setItem(row, 4, QTableWidgetItem(str(s['notes'] or "")))

            btns_widget = QWidget()
            btns_layout = QHBoxLayout(btns_widget)
            btns_layout.setContentsMargins(2, 2, 2, 2)

            details_btn = QPushButton("تفاصيل")
            details_btn.clicked.connect(lambda _, supplier=s: self.show_details(supplier))

            edit_btn = QPushButton("تعديل")
            edit_btn.clicked.connect(lambda _, supplier=s: self.show_edit_dialog(supplier))

            delete_btn = QPushButton()
            delete_btn.setIcon(qta.icon("fa5s.trash-alt", color="white"))
            delete_btn.setFixedSize(30, 30)
            delete_btn.setStyleSheet("background-color: #e74c3c; border-radius: 5px;")
            delete_btn.clicked.connect(lambda _, supplier=s: self.handle_delete(supplier))

            btns_layout.addWidget(details_btn)
            btns_layout.addWidget(edit_btn)
            btns_layout.addWidget(delete_btn)
            self.table.setCellWidget(row, 5, btns_widget)

    def show_details(self, s):
        stats = self.controller.model.get_stats(s['id'])
        products = self.controller.model.get_products(s['id'])
        from views.supplier_details_dialog import SupplierDetailsDialog
        dialog = SupplierDetailsDialog(s, stats, products, self)
        dialog.exec()

    def handle_delete(self, s):
        from utils.auth import AuthManager
        if not AuthManager.has_permission('suppliers', 'delete'):
            QMessageBox.warning(self, "تنبيه", "لا تملك صلاحية الحذف")
            return

        if QMessageBox.question(self, "تأكيد", f"حذف المورد '{s['name']}'؟") == QMessageBox.Yes:
            self.controller.model.update(s['id'], {"is_deleted": 1})
            self.refresh()

    def handle_search(self):
        term = self.search_input.text()
        if term:
            self.refresh(self.controller.search_suppliers(term))
        else:
            self.refresh()

    def show_add_dialog(self):
        from PySide6.QtWidgets import QDialog, QFormLayout
        from utils.validator import Validator
        dialog = QDialog(self)
        dialog.setWindowTitle("إضافة مورد")
        d_layout = QFormLayout(dialog)

        name = QLineEdit()
        Validator.setup_strict_validation(name, "name")
        phone = QLineEdit()
        Validator.setup_strict_validation(phone, "phone")
        email = QLineEdit()
        address = QLineEdit()
        notes = QLineEdit()

        d_layout.addRow("الاسم:", name)
        d_layout.addRow("الهاتف:", phone)
        d_layout.addRow("البريد:", email)
        d_layout.addRow("العنوان:", address)
        d_layout.addRow("ملاحظات:", notes)

        save = QPushButton("حفظ")
        save.clicked.connect(lambda: self.save_supplier(dialog, {
            "name": name.text(), "phone": phone.text(), "email": email.text(),
            "address": address.text(), "notes": notes.text()
        }))
        d_layout.addRow(save)
        dialog.exec()

    def save_supplier(self, dialog, data):
        if not data['name']:
            QMessageBox.warning(self, "تنبيه", "الاسم مطلوب")
            return
        self.controller.add_supplier(data)
        dialog.accept()
        self.refresh()

    def show_edit_dialog(self, supplier):
        from utils.auth import AuthManager
        if not AuthManager.has_permission('suppliers', 'edit'):
            QMessageBox.warning(self, "تنبيه", "لا تملك صلاحية التعديل")
            return

        from PySide6.QtWidgets import QDialog, QFormLayout
        from utils.validator import Validator
        dialog = QDialog(self)
        dialog.setWindowTitle("تعديل مورد")
        d_layout = QFormLayout(dialog)

        name = QLineEdit(supplier['name'])
        Validator.setup_strict_validation(name, "name")
        phone = QLineEdit(supplier['phone'] or "")
        Validator.setup_strict_validation(phone, "phone")
        email = QLineEdit(supplier['email'] or "")
        address = QLineEdit(supplier['address'] or "")
        notes = QLineEdit(supplier['notes'] or "")

        d_layout.addRow("الاسم:", name)
        d_layout.addRow("الهاتف:", phone)
        d_layout.addRow("البريد:", email)
        d_layout.addRow("العنوان:", address)
        d_layout.addRow("ملاحظات:", notes)

        save = QPushButton("تعديل")
        save.clicked.connect(lambda: self.update_supplier(dialog, supplier['id'], {
            "name": name.text(), "phone": phone.text(), "email": email.text(),
            "address": address.text(), "notes": notes.text()
        }))
        d_layout.addRow(save)
        dialog.exec()

    def update_supplier(self, dialog, s_id, data):
        if not data['name']:
            QMessageBox.warning(self, "تنبيه", "الاسم مطلوب")
            return
        self.controller.update_supplier(s_id, data)
        dialog.accept()
        self.refresh()

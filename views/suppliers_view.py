from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableView,
                             QPushButton, QLineEdit, QLabel,
                             QHeaderView, QGroupBox, QMessageBox)
from PySide6.QtCore import Qt, QThreadPool
import qtawesome as qta
from utils.auth import AuthManager
from views_components.enterprise_table_model import EnterpriseTableModel
from workers.worker import Worker

class SuppliersView(QWidget):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.threadpool = QThreadPool()
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
        self.view = QTableView()
        self.view.setEditTriggers(QTableView.NoEditTriggers)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.view)

        self.headers = ["name", "phone", "email", "address"]
        self.model = EnterpriseTableModel([], self.headers)
        self.view.setModel(self.model)

        self.refresh()

    def refresh(self, suppliers=None):
        if suppliers:
            self.model.update_data(suppliers)
            return

        worker = Worker(self.service.get_all)
        worker.signals.result.connect(self.on_data_loaded)
        self.threadpool.start(worker)

    def on_data_loaded(self, suppliers):
        data = [
            {"name": s.name, "phone": s.phone, "email": s.email, "address": s.address}
            for s in suppliers
        ]
        self.model.update_data(data)

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

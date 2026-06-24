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
            self.on_data_loaded(suppliers)
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

    def handle_search(self):
        term = self.search_input.text()
        if term:
            results = self.service.supplier_repo.db.query(self.service.supplier_repo.model).filter(
                self.service.supplier_repo.model.name.ilike(f"%{term}%"),
                self.service.supplier_repo.model.is_deleted == False
            ).all()
            self.refresh(results)
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

        d_layout.addRow("الاسم:", name)
        d_layout.addRow("الهاتف:", phone)
        d_layout.addRow("البريد:", email)
        d_layout.addRow("العنوان:", address)

        save = QPushButton("حفظ")
        save.clicked.connect(lambda: self.save_supplier(dialog, {
            "name": name.text(), "phone": phone.text(), "email": email.text(),
            "address": address.text()
        }))
        d_layout.addRow(save)
        dialog.exec()

    def save_supplier(self, dialog, data):
        if not data['name']:
            QMessageBox.warning(self, "تنبيه", "الاسم مطلوب")
            return
        self.service.create_supplier(data)
        dialog.accept()
        self.refresh()

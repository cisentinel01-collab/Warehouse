from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableView,
                             QPushButton, QLineEdit, QLabel,
                             QHeaderView, QDialog, QFormLayout, QComboBox,
                             QSpinBox, QMessageBox, QFileDialog, QInputDialog)
from PySide6.QtCore import Qt, Signal, QTimer, QThreadPool
import qtawesome as qta
import os
from app.utils.auth import AuthManager
from app.utils.translation_manager import tr
from app.views.components.enterprise_table_model import EnterpriseTableModel
from app.workers.worker import Worker

class ItemsView(QWidget):
    data_changed = Signal()

    def __init__(self, item_service):
        super().__init__()
        self.service = item_service
        self.threadpool = QThreadPool()
        self.current_page = 0
        self.page_size = 50

        # Search debounce timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Toolbar
        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("بحث عن صنف (اسم، كود، فئة)...")
        self.search_input.textChanged.connect(self.handle_search)
        toolbar.addWidget(self.search_input)

        # Pagination Controls
        pagination_layout = QHBoxLayout()
        self.prev_btn = QPushButton()
        self.prev_btn.setIcon(qta.icon("fa5s.chevron-right", color="#1a2a6c"))
        self.prev_btn.setFixedSize(35, 35)
        self.prev_btn.clicked.connect(self.prev_page)

        self.next_btn = QPushButton()
        self.next_btn.setIcon(qta.icon("fa5s.chevron-left", color="#1a2a6c"))
        self.next_btn.setFixedSize(35, 35)
        self.next_btn.clicked.connect(self.next_page)

        self.page_label = QLabel(f"صفحة {self.current_page + 1}")
        self.page_label.setStyleSheet("font-weight: bold; margin: 0 10px;")

        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.prev_btn)
        toolbar.addLayout(pagination_layout)

        add_btn = QPushButton("إضافة صنف جديد")
        add_btn.setObjectName("PrimaryButton")
        add_btn.setIcon(qta.icon("fa5s.plus", color="white"))
        add_btn.setEnabled(AuthManager.has_permission('items', 'add'))
        add_btn.clicked.connect(self.show_add_dialog)
        toolbar.addWidget(add_btn)

        import_btn = QPushButton("استيراد من Excel")
        import_btn.setObjectName("SecondaryButton")
        import_btn.setEnabled(AuthManager.has_permission('items', 'add'))
        import_btn.clicked.connect(self.handle_import)
        toolbar.addWidget(import_btn)

        layout.addLayout(toolbar)

        # Table
        self.view = QTableView()
        self.view.setEditTriggers(QTableView.NoEditTriggers)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.view)

        self.headers = ["code", "name", "category", "unit", "current_stock", "min_stock"]
        self.model = EnterpriseTableModel([], self.headers)
        self.view.setModel(self.model)

        self.refresh()

    def refresh(self, items=None):
        if items:
            self.model.update_data(items)
            return

        worker = Worker(self.service.get_items, skip=self.current_page * self.page_size, limit=self.page_size)
        worker.signals.result.connect(self.on_data_loaded)
        self.threadpool.start(worker)

    def on_data_loaded(self, items):
        # Convert ORM objects to dict for the model (simplified for ERP architecture)
        data = [
            {
                "code": i.code, "name": i.name, "category": i.category,
                "unit": i.unit, "current_stock": i.current_stock, "min_stock": i.min_stock
            } for i in items
        ]
        self.model.update_data(data)
        self.page_label.setText(f"{tr.get_text('page')} {self.current_page + 1}")
        self.next_btn.setEnabled(len(items) == self.page_size)
        self.prev_btn.setEnabled(self.current_page > 0)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.refresh()

    def next_page(self):
        self.current_page += 1
        self.refresh()

    def handle_delete(self, item):
        if not AuthManager.has_permission('items', 'delete'):
            QMessageBox.warning(self, "تنبيه", "لا تملك صلاحية الحذف")
            return

        if QMessageBox.question(self, "تأكيد", f"هل أنت متأكد من حذف '{item['name']}'؟") == QMessageBox.Yes:
            self.controller.delete_item(item['id'])
            self.refresh()
            self.data_changed.emit()

    def handle_search(self):
        # Debounce search
        self.search_timer.start(300)

    def perform_search(self):
        term = self.search_input.text()
        if term:
            self.current_page = 0 # Reset to first page of search results
            items = self.controller.search_items(term)
            # For search we currently load all or let model handle it,
            # but usually search is specific enough.
            self.refresh(items)
        else:
            self.current_page = 0
            self.refresh()

    def show_add_dialog(self):
        dialog = ItemDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.controller.add_item(data)
            self.refresh()
            self.data_changed.emit()

    def show_edit_dialog(self, item):
        if not AuthManager.has_permission('items', 'can_edit'):
            QMessageBox.warning(self, "تنبيه", "لا تملك صلاحية التعديل")
            return

        dialog = ItemDialog(self, item)
        if dialog.exec():
            data = dialog.get_data()
            self.controller.update_item(item['id'], data)
            self.refresh()
            self.data_changed.emit()

    def handle_import(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "اختر ملف Excel", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            try:
                from utils.excel_gen import ExcelGenerator
                items = ExcelGenerator().import_items(file_path)
                for item in items:
                    self.controller.add_item(item)
                self.refresh()
                QMessageBox.information(self, "نجاح", f"تم استيراد {len(items)} صنف بنجاح")
                self.data_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل الاستيراد: {str(e)}")

class ItemDialog(QDialog):
    def __init__(self, parent=None, item_data=None):
        super().__init__(parent)
        self.item_data = item_data
        self.setWindowTitle("تعديل بيانات الصنف" if item_data else "إضافة صنف جديد")
        self.resize(500, 500)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()
        if item_data:
            self.load_data()

    def setup_ui(self):
        layout = QFormLayout(self)
        from utils.validator import Validator

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("مثال: ITEM-101")

        # QR Scan button inside dialog
        code_row = QHBoxLayout()
        code_row.addWidget(self.code_input)
        scan_btn = QPushButton()
        scan_btn.setIcon(qta.icon("fa5s.qrcode", color="#1a2a6c"))
        scan_btn.setFixedSize(40, 40)
        scan_btn.setToolTip("مسح كود QR تلقائياً")
        scan_btn.clicked.connect(self.handle_scan)
        code_row.addWidget(scan_btn)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("أدخل اسم الصنف")
        Validator.setup_strict_validation(self.name_input, "name")

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("مثال: قطع غيار")
        Validator.setup_strict_validation(self.category_input, "name")

        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("مثال: قطعة")
        Validator.setup_strict_validation(self.unit_input, "name")

        self.min_stock_input = QSpinBox()
        self.min_stock_input.setMaximum(1000000)

        self.location_combo = QComboBox()
        from models.location import Location
        locations = Location().get_all()
        for loc in locations:
            self.location_combo.addItem(loc['name'], loc['id'])

        self.supplier_combo = QComboBox()
        from models.supplier import Supplier
        suppliers = Supplier().get_all()
        for s in suppliers:
            self.supplier_combo.addItem(s['name'], s['id'])

        layout.addRow("كود الصنف:", code_row)
        layout.addRow("اسم الصنف:", self.name_input)
        layout.addRow("الفئة:", self.category_input)
        layout.addRow("الوحدة:", self.unit_input)
        layout.addRow("المورد الافتراضي:", self.supplier_combo)
        layout.addRow("موقع التخزين:", self.location_combo)

        min_stock_layout = QHBoxLayout()
        min_stock_layout.addWidget(self.min_stock_input)
        min_stock_layout.addStretch()
        layout.addRow("الحد الأدنى:", min_stock_layout)

        btns = QHBoxLayout()
        save_btn = QPushButton("حفظ")
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addRow(btns)

    def handle_scan(self):
        code, ok = QInputDialog.getText(self, "مسح QR", "يرجى مسح كود QR الآن:")
        if ok and code:
            self.code_input.setText(code)

    def load_data(self):
        self.code_input.setText(str(self.item_data['code']))
        self.name_input.setText(str(self.item_data['name']))
        self.category_input.setText(str(self.item_data['category'] or ""))
        self.unit_input.setText(str(self.item_data['unit'] or ""))
        self.min_stock_input.setValue(self.item_data['min_stock'])
        if self.item_data.get('location_id'):
            index = self.location_combo.findData(self.item_data['location_id'])
            if index >= 0:
                self.location_combo.setCurrentIndex(index)
        if self.item_data.get('supplier_id'):
            index = self.supplier_combo.findData(self.item_data['supplier_id'])
            if index >= 0:
                self.supplier_combo.setCurrentIndex(index)

    def accept(self):
        from utils.validator import Validator
        if not Validator.is_not_empty(self.code_input.text()) or \
           not Validator.is_not_empty(self.name_input.text()):
            QMessageBox.warning(self, "تنبيه", "يرجى ملأ الخانات الأساسية (الكود والاسم)")
            return
        super().accept()

    def get_data(self):
        return {
            "code": self.code_input.text(),
            "name": self.name_input.text(),
            "category": self.category_input.text(),
            "unit": self.unit_input.text(),
            "location_id": self.location_combo.currentData(),
            "supplier_id": self.supplier_combo.currentData(),
            "min_stock": self.min_stock_input.value()
        }

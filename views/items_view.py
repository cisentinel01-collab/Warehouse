from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                             QHeaderView, QDialog, QFormLayout, QComboBox,
                             QSpinBox, QMessageBox, QFileDialog, QInputDialog)
from PySide6.QtCore import Qt, Signal, QTimer
import qtawesome as qta
import os
from utils.auth import AuthManager

class ItemsView(QWidget):
    data_changed = Signal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
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
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["الكود", "الاسم", "الفئة", "الوحدة", "الموقع", "الكمية", "الحد الأدنى", "إجراءات"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) # Name stretches
        self.table.horizontalHeader().setDefaultSectionSize(120)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self, items=None):
        self.table.setUpdatesEnabled(False)
        if items is None:
            offset = self.current_page * self.page_size
            items = self.controller.get_all_items(limit=self.page_size, offset=offset)

        self.table.setRowCount(0)
        self.page_label.setText(f"صفحة {self.current_page + 1}")

        # Disable next if we got fewer items than page size
        self.next_btn.setEnabled(len(items) == self.page_size)
        self.prev_btn.setEnabled(self.current_page > 0)

        for item in items:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Ensure items are readable by creating QTableWidgetItem explicitly
            self.table.setItem(row, 0, QTableWidgetItem(str(item['code'])))
            self.table.setItem(row, 1, QTableWidgetItem(str(item['name'])))
            self.table.setItem(row, 2, QTableWidgetItem(str(item['category'] or "")))
            self.table.setItem(row, 3, QTableWidgetItem(str(item['unit'] or "")))
            self.table.setItem(row, 4, QTableWidgetItem(str(item['location_name'] or "")))
            self.table.setItem(row, 5, QTableWidgetItem(str(item['current_stock'])))
            self.table.setItem(row, 6, QTableWidgetItem(str(item['min_stock'])))

            btns_widget = QWidget()
            btns_layout = QHBoxLayout(btns_widget)
            btns_layout.setContentsMargins(2, 2, 2, 2)

            edit_btn = QPushButton("تعديل")
            edit_btn.setStyleSheet("background-color: #f39c12; color: white; border-radius: 5px; font-weight: bold;")
            edit_btn.setEnabled(AuthManager.has_permission('items', 'can_edit'))
            edit_btn.clicked.connect(lambda _, i=item: self.show_edit_dialog(i))

            delete_btn = QPushButton()
            delete_btn.setIcon(qta.icon("fa5s.trash-alt", color="white"))
            delete_btn.setFixedSize(30, 30)
            delete_btn.setStyleSheet("background-color: #e74c3c; border-radius: 5px;")
            delete_btn.setEnabled(AuthManager.has_permission('items', 'delete'))
            delete_btn.clicked.connect(lambda _, i=item: self.handle_delete(i))

            btns_layout.addWidget(edit_btn)
            btns_layout.addWidget(delete_btn)
            self.table.setCellWidget(row, 7, btns_widget)
        self.table.setUpdatesEnabled(True)

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

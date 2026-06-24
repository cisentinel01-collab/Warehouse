from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt

class SupplierDetailsDialog(QDialog):
    def __init__(self, supplier, stats, products, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"تفاصيل المورد: {supplier['name']}")
        self.resize(700, 500)
        self.setLayoutDirection(Qt.RightToLeft)
        self.supplier = supplier
        self.stats = stats
        self.products = products
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        info_label = QLabel(f"الاسم: {self.supplier['name']}\nالهاتف: {self.supplier['phone']}\nالعنوان: {self.supplier['address']}")
        layout.addWidget(info_label)

        layout.addWidget(QLabel("الأصناف الموردة:"))
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["الصنف", "الكمية الكلية", "آخر توريد"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for p in self.products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(p['name'])))
            self.table.setItem(row, 1, QTableWidgetItem(str(p['total_qty'])))
            self.table.setItem(row, 2, QTableWidgetItem(str(p['last_delivery'])))

        layout.addWidget(self.table)

        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QPushButton
from PySide6.QtCore import Qt

class SupplierDetailsDialog(QDialog):
    def __init__(self, supplier, stats, products, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"تفاصيل المورد: {supplier['name']}")
        self.resize(800, 600)
        self.setStyleSheet("background-color: #000000; color: white;")

        layout = QVBoxLayout(self)

        # Stats Header
        stats_layout = QHBoxLayout()
        self.add_stat(stats_layout, "عدد الأصناف", str(stats.get('product_count') or 0))
        val = stats.get('total_purchase_value') or 0
        self.add_stat(stats_layout, "إجمالي المشتريات", f"{float(val):,.2f}")
        self.add_stat(stats_layout, "آخر توريد", str(stats.get('last_purchase_date') or 'N/A'))
        layout.addLayout(stats_layout)

        # Products Table
        table_label = QLabel("قائمة الأصناف الموردة:")
        table_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        layout.addWidget(table_label)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["الصنف", "الكود", "آخر سعر شراء", "المخزون المتاح"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setRowCount(len(products))

        for r, p in enumerate(products):
            self.table.setItem(r, 0, QTableWidgetItem(str(p.get('name') or "")))
            self.table.setItem(r, 1, QTableWidgetItem(str(p.get('code') or "")))
            last_price = p.get('last_price') or 0
            self.table.setItem(r, 2, QTableWidgetItem(f"{float(last_price):,.2f}"))
            self.table.setItem(r, 3, QTableWidgetItem(str(p.get('current_stock') or 0)))

        layout.addWidget(self.table)

        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def add_stat(self, layout, title, value):
        frame = QFrame()
        frame.setStyleSheet("border: 1px solid #d4af37; border-radius: 8px; padding: 10px;")
        l = QVBoxLayout(frame)
        l.addWidget(QLabel(title), 0, Qt.AlignCenter)
        val = QLabel(value)
        val.setStyleSheet("font-size: 18px; font-weight: bold; color: #d4af37;")
        l.addWidget(val, 0, Qt.AlignCenter)
        layout.addWidget(frame)

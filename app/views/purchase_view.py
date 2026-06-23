from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                             QHeaderView, QMessageBox, QTabWidget)
from PySide6.QtCore import Qt
import qtawesome as qta
from controllers.purchase_controller import PurchaseController

class PurchaseView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = PurchaseController()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Toolbar
        toolbar = QHBoxLayout()

        suggest_btn = QPushButton("توليد مقترحات الشراء")
        suggest_btn.setObjectName("GoldButton")
        suggest_btn.setIcon(qta.icon("fa5s.magic", color="black"))
        from utils.auth import AuthManager
        if not AuthManager.has_permission('purchase', 'add'):
            suggest_btn.setEnabled(False)

        suggest_btn.clicked.connect(self.handle_suggest)
        toolbar.addWidget(suggest_btn)

        refresh_btn = QPushButton("تحديث")
        refresh_btn.setIcon(qta.icon("fa5s.sync", color="white"))
        refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(refresh_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["رقم الطلب", "المورد", "التاريخ", "الإجمالي", "الحالة", "إجراءات"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self):
        pos = self.controller.get_pos()
        self.table.setRowCount(0)
        for po in pos:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(po['po_number'])))
            self.table.setItem(row, 1, QTableWidgetItem(str(po['supplier_name'])))
            self.table.setItem(row, 2, QTableWidgetItem(str(po['date'])))
            self.table.setItem(row, 3, QTableWidgetItem(f"{po['total']:,.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(po['status'])))

            pdf_btn = QPushButton("PDF")
            pdf_btn.clicked.connect(lambda _, pid=po['id']: self.view_pdf(pid))
            self.table.setCellWidget(row, 5, pdf_btn)

    def handle_suggest(self):
        created = self.controller.generate_suggested_pos()
        if created:
            QMessageBox.information(self, "نجاح", f"تم إنشاء {len(created)} أوامر شراء جديدة بنجاح بناءً على النواقص")
            self.refresh()
        else:
            QMessageBox.information(self, "تنبيه", "لا توجد نواقص تتطلب إعادة الطلب حالياً")

    def view_pdf(self, po_id):
        path = self.controller.generate_po_pdf(po_id)
        from views.print_preview import PrintPreviewDialog
        dialog = PrintPreviewDialog(path, self)
        dialog.exec()

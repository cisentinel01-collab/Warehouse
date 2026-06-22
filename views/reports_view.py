from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QPushButton, QLabel, QGridLayout, QMessageBox)
from PySide6.QtCore import Qt

class ReportsView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Reports Grid
        grid = QGridLayout()

        self.create_report_item(grid, "تقرير المخزون الحالي", "fa5s.boxes", self.handle_inv_pdf, self.handle_inv_excel, 0, 0)
        self.create_report_item(grid, "تقرير الوارد", "fa5s.file-import", self.handle_in_pdf, self.handle_in_excel, 0, 1)
        self.create_report_item(grid, "تقرير الصادر", "fa5s.file-export", self.handle_out_pdf, self.handle_out_excel, 1, 0)
        self.create_report_item(grid, "تقرير النواقص", "fa5s.shopping-basket", self.handle_inv_pdf, None, 1, 1)
        self.create_report_item(grid, "تقرير منتهى الصلاحية", "fa5s.calendar-times", self.handle_expired_pdf, None, 2, 0)
        self.create_report_item(grid, "سجل نشاط المستخدمين", "fa5s.user-shield", self.handle_audit_pdf, None, 2, 1)

        layout.addLayout(grid)
        layout.addStretch()

    def create_report_item(self, grid, title, icon, pdf_func, excel_func, r, c):
        group = QGroupBox(title)
        l = QVBoxLayout(group)

        pdf_btn = QPushButton("تصدير PDF")
        pdf_btn.clicked.connect(pdf_func)
        l.addWidget(pdf_btn)

        if excel_func:
            excel_btn = QPushButton("تصدير Excel")
            excel_btn.clicked.connect(excel_func)
            l.addWidget(excel_btn)

        grid.addWidget(group, r, c)

    def handle_inv_pdf(self):
        path = self.controller.export_inventory_to_pdf()
        QMessageBox.information(self, "نجاح", f"تم الحفظ في {path}")

    def handle_inv_excel(self):
        path = self.controller.export_inventory_to_excel()
        QMessageBox.information(self, "نجاح", f"تم الحفظ في {path}")

    def handle_in_pdf(self):
        path = self.controller.export_movements_to_pdf("IN")
        QMessageBox.information(self, "نجاح", f"تم الحفظ في {path}")

    def handle_in_excel(self):
        path = self.controller.export_movements_to_excel("IN")
        QMessageBox.information(self, "نجاح", f"تم الحفظ في {path}")

    def handle_out_pdf(self):
        path = self.controller.export_movements_to_pdf("OUT")
        QMessageBox.information(self, "نجاح", f"تم الحفظ في {path}")

    def handle_out_excel(self):
        path = self.controller.export_movements_to_excel("OUT")
        QMessageBox.information(self, "نجاح", f"تم الحفظ في {path}")

    def handle_audit_pdf(self):
        path = self.controller.export_audit_to_pdf()
        QMessageBox.information(self, "نجاح", f"تم الحفظ في {path}")

    def handle_expired_pdf(self):
        path = self.controller.export_expiry_to_pdf(expired_only=True)
        QMessageBox.information(self, "نجاح", f"تم الحفظ في {path}")

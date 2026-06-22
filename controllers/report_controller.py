from models.item import Item
from models.movement import Movement
from models.supplier import Supplier
from models.audit_log import AuditLog
from utils.excel_gen import ExcelGenerator
from models.settings import Settings
from utils.pdf_gen import PDFGenerator
import datetime

class ReportController:
    def __init__(self):
        self.item_model = Item()
        self.movement_model = Movement()
        self.supplier_model = Supplier()
        self.audit_log = AuditLog()
        self.excel_gen = ExcelGenerator()
        self.pdf_gen = PDFGenerator()
        self.settings_model = Settings()

    def export_inventory_to_excel(self):
        items = self.item_model.get_all_with_location()
        headers = ["كود الصنف", "اسم الصنف", "الفئة", "الموقع", "الكمية الحالية", "الحد الأدنى"]
        data = [[i['code'], i['name'], i['category'], i['location_name'], i['current_stock'], i['min_stock']] for i in items]

        filename = f"reports/inventory_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx"
        self.excel_gen.export_data(filename, headers, data, "تقرير المخزون الحالي")
        return filename

    def export_movements_to_excel(self, type=None, start_date=None, end_date=None):
        movements = self.movement_model.get_history(type, start_date, end_date)
        headers = ["التاريخ", "النوع", "الرقم المرجعي", "المورد/المستلم", "ملاحظات"]
        data = []
        for m in movements:
            party = m['supplier_name'] if m['type'] == 'IN' else m['receiver_name']
            data.append([m['date'], "وارد" if m['type'] == 'IN' else "صادر", m['reference_no'], party, m['notes']])

        title = "تقرير حركة المخزن"
        if type == 'IN': title = "تقرير الوارد"
        elif type == 'OUT': title = "تقرير الصادر"

        filename = f"reports/movements_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx"
        self.excel_gen.export_data(filename, headers, data, title)
        return filename

    def export_inventory_to_pdf(self):
        items = self.item_model.get_all_with_location()
        headers = ["كود الصنف", "اسم الصنف", "الفئة", "الموقع", "الكمية", "الحد الأدنى"]
        data = [[i['code'], i['name'], i['category'], i['location_name'], i['current_stock'], i['min_stock']] for i in items]
        filename = f"reports/inventory_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
        self.pdf_gen.generate_report(filename, "تقرير المخزون الحالي", headers, data, self.settings_model.get_settings())
        return filename

    def export_movements_to_pdf(self, type=None):
        movements = self.movement_model.get_history(type)
        headers = ["التاريخ", "النوع", "الرقم المرجعي", "المورد/المستلم", "الإجمالي"]
        data = []
        for m in movements:
            party = m['supplier_name'] if m['type'] == 'IN' else m['receiver_name']
            data.append([m['date'], "وارد" if m['type'] == 'IN' else "صادر", m['reference_no'], party, m['final_total']])

        title = "تقرير حركة المخزن"
        if type == 'IN': title = "تقرير الوارد"
        elif type == 'OUT': title = "تقرير الصادر"
        filename = f"reports/movements_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
        self.pdf_gen.generate_report(filename, title, headers, data, self.settings_model.get_settings())
        return filename

    def export_audit_to_pdf(self):
        logs = self.audit_log.get_logs(500)
        headers = ["التاريخ", "المستخدم", "العملية", "الجدول", "المعرف"]
        data = [[l['timestamp'], l['user_name'], l['action'], l['table_name'], l['record_id']] for l in logs]
        filename = f"reports/audit_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
        self.pdf_gen.generate_report(filename, "سجل نشاط المستخدمين", headers, data, self.settings_model.get_settings())
        return filename

    def export_expiry_to_pdf(self, expired_only=False):
        from models.batch import Batch
        batch_model = Batch()
        if expired_only:
            batches = batch_model.get_expired()
            title = "تقرير الأصناف منتهية الصلاحية"
        else:
            batches = batch_model.get_expiring_soon(6)
            title = "تقرير الأصناف التي ستنتهي قريباً"

        headers = ["الصنف", "التشغيلة", "الكمية", "تاريخ الانتهاء"]
        data = [[b['item_name'], b['batch_number'], b['quantity'], str(b['expiry_date'])] for b in batches]
        filename = f"reports/expiry_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
        self.pdf_gen.generate_report(filename, title, headers, data, self.settings_model.get_settings())
        return filename

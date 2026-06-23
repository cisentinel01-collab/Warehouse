from models.movement import Movement
from models.audit_log import AuditLog
from models.settings import Settings
from utils.auth import AuthManager
from utils.pdf_gen import PDFGenerator
import datetime

class StockController:
    def __init__(self):
        self.movement_model = Movement()
        self.audit_log = AuditLog()
        self.settings_model = Settings()
        self.pdf_gen = PDFGenerator()

    def calculate_totals(self, items_list, discount_percent=0):
        subtotal = sum(item['quantity'] * item.get('price', 0) for item in items_list)
        discount_amount = (subtotal * discount_percent) / 100
        final_total = subtotal - discount_amount
        return subtotal, discount_amount, final_total

    def generate_invoice_no(self, type):
        prefix = "IN" if type == "IN" else "OUT"
        timestamp = datetime.datetime.now().strftime("%Y%m%d")

        # PostgreSQL: Cast timestamp to text before using LIKE
        query = "SELECT COUNT(*) as count FROM movements WHERE type = %s AND CAST(date AS TEXT) LIKE %s"
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        res = self.movement_model.db.execute_query(query, (type, f"{today}%"))
        seq = (res[0]['count'] if res else 0) + 1

        return f"{prefix}-{timestamp}-{seq:04d}"

    def receive_stock(self, movement_data, items_list):
        if 'date' not in movement_data:
            movement_data['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not movement_data.get('reference_no'):
            movement_data['reference_no'] = self.generate_invoice_no('IN')

        movement_data['type'] = 'IN'

        subtotal, discount_amount, final_total = self.calculate_totals(items_list, movement_data.get('discount_percent', 0))
        movement_data['subtotal'] = subtotal
        movement_data['discount_amount'] = discount_amount
        movement_data['final_total'] = final_total

        movement_id = self.movement_model.create_movement(movement_data, items_list)

        user = AuthManager.get_current_user()
        self.audit_log.log(user['id'] if user else None, "Stock In", "movements", movement_id)

        self.generate_movement_pdf(movement_id)
        return movement_id, [] # No low stock warning for receiving

    def issue_stock(self, movement_data, items_list):
        if 'date' not in movement_data:
            movement_data['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not movement_data.get('reference_no'):
            movement_data['reference_no'] = self.generate_invoice_no('OUT')

        movement_data['type'] = 'OUT'

        subtotal, discount_amount, final_total = self.calculate_totals(items_list, movement_data.get('discount_percent', 0))
        movement_data['subtotal'] = subtotal
        movement_data['discount_amount'] = discount_amount
        movement_data['final_total'] = final_total

        movement_id = self.movement_model.create_movement(movement_data, items_list)

        user = AuthManager.get_current_user()
        self.audit_log.log(user['id'] if user else None, "Stock Out", "movements", movement_id)

        self.generate_movement_pdf(movement_id)

        # Check for low stock after issuing
        low_items = []
        from models.item import Item
        item_model = Item()
        for i_data in items_list:
            item = item_model.get_by_id(i_data['item_id'])
            if item['current_stock'] <= item['min_stock']:
                low_items.append(item['name'])

        return movement_id, low_items

    def generate_movement_pdf(self, movement_id):
        movement = self.movement_model.get_by_id(movement_id)
        if movement['supplier_id']:
            from models.supplier import Supplier
            supplier = Supplier().get_by_id(movement['supplier_id'])
            movement = dict(movement)
            movement['supplier_name'] = supplier['name'] if supplier else ""

        items = self.movement_model.get_movement_details(movement_id)
        company_info = self.settings_model.get_settings()

        filename = f"reports/movement_{movement_id}.pdf"
        self.pdf_gen.generate_invoice(filename, movement, items, company_info)
        return filename

    def get_movement_history(self, **kwargs):
        return self.movement_model.get_history(**kwargs)

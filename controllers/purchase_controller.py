from models.purchase_order import PurchaseOrder
from models.item import Item
from models.supplier import Supplier
from utils.pdf_gen import PDFGenerator
from models.settings import Settings

class PurchaseController:
    def __init__(self):
        self.po_model = PurchaseOrder()
        self.item_model = Item()
        self.supplier_model = Supplier()
        self.pdf_gen = PDFGenerator()
        self.settings_model = Settings()

    def get_pos(self):
        return self.po_model.get_all_with_supplier()

    def generate_po_pdf(self, po_id):
        po = self.po_model.get_by_id(po_id)
        supplier = self.supplier_model.get_by_id(po['supplier_id'])
        items = self.po_model.get_details(po_id)
        settings = self.settings_model.get_settings()

        filename = f"reports/PO_{po['po_number']}.pdf"

        # We'll use a modified invoice template for PO
        data = {
            "type": "PO",
            "report_title": f"امر شراء رقم: {po['po_number']}",
            "reference_no": po['po_number'],
            "date": str(po['date']),
            "supplier_name": supplier['name'],
            "subtotal": po['total'],
            "discount_amount": 0,
            "discount_percent": 0,
            "final_total": po['total'],
            "notes": f"حالة الطلب: {po['status']}"
        }

        # Prepare items for reportlab
        report_items = []
        for i in items:
            report_items.append({
                "item_name": i['item_name'],
                "item_code": i['item_code'],
                "quantity": i['quantity'],
                "price": i['unit_price'],
                "unit": "" # PO items don't have unit in schema yet, adding it as blank
            })

        self.pdf_gen.generate_invoice(filename, data, report_items, settings)
        return filename

    def generate_suggested_pos(self):
        # Group low stock items by supplier
        low_stock = self.item_model.get_low_stock()
        by_supplier = {}
        for item in low_stock:
            s_id = item['supplier_id']
            if not s_id: continue
            if s_id not in by_supplier:
                by_supplier[s_id] = []
            by_supplier[s_id].append(item)

        created_pos = []
        for s_id, items in by_supplier.items():
            po_items = []
            for item in items:
                # Suggest reordering up to 2x min_stock
                suggested_qty = (item['min_stock'] * 2) - item['current_stock']
                if suggested_qty <= 0: suggested_qty = 10 # Fallback

                # Try to get last purchase price
                last_price_res = self.item_model.db.execute_query("""
                    SELECT price FROM movement_items mi
                    JOIN movements m ON mi.movement_id = m.id
                    WHERE mi.item_id = %s AND m.type = 'IN'
                    ORDER BY m.date DESC LIMIT 1
                """, (item['id'],))
                price = last_price_res[0]['price'] if last_price_res else 0

                po_items.append({
                    "item_id": item['id'],
                    "quantity": int(suggested_qty),
                    "unit_price": float(price)
                })

            po_id = self.po_model.create_po(s_id, po_items)
            created_pos.append(po_id)

        return created_pos

from models.base_model import BaseModel

class PurchaseOrder(BaseModel):
    table_name = "purchase_orders"

    def create_po(self, supplier_id, items):
        # Generate PO number
        from datetime import datetime
        po_number = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        total = sum(i['quantity'] * i['unit_price'] for i in items)

        po_id = self.create({
            "supplier_id": supplier_id,
            "po_number": po_number,
            "total": total,
            "status": "pending"
        })

        for item in items:
            self.db.execute_query("""
                INSERT INTO po_items (po_id, item_id, quantity, unit_price, total)
                VALUES (%s, %s, %s, %s, %s)
            """, (po_id, item['item_id'], item['quantity'], item['unit_price'], item['quantity'] * item['unit_price']), commit=True)

        return po_id

    def get_details(self, po_id):
        query = """
            SELECT pi.*, i.name as item_name, i.code as item_code
            FROM po_items pi
            JOIN items i ON pi.item_id = i.id
            WHERE pi.po_id = %s
        """
        return self.db.execute_query(query, (po_id,))

    def get_all_with_supplier(self):
        query = """
            SELECT po.*, s.name as supplier_name
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.id
            ORDER BY po.created_at DESC
        """
        return self.db.execute_query(query)

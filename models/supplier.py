from models.base_model import BaseModel

class Supplier(BaseModel):
    table_name = "suppliers"

    def search(self, term):
        query = f"SELECT * FROM {self.table_name} WHERE is_deleted = 0 AND (name LIKE  %s  OR phone LIKE  %s  OR email LIKE  %s )"
        pattern = f"%{term}%"
        return self.db.execute_query(query, (pattern, pattern, pattern))

    def get_stats(self, supplier_id):
        query = """
            SELECT
                (SELECT COUNT(*) FROM items WHERE supplier_id = %s AND is_deleted = 0) as product_count,
                (SELECT SUM(final_total) FROM movements WHERE supplier_id = %s AND type = 'IN') as total_purchase_value,
                (SELECT MAX(date) FROM movements WHERE supplier_id = %s AND type = 'IN') as last_purchase_date
        """
        results = self.db.execute_query(query, (supplier_id, supplier_id, supplier_id))
        return results[0] if results else {}

    def get_products(self, supplier_id):
        query = """
            SELECT name, current_stock, code,
            (SELECT price FROM movement_items mi
             JOIN movements m ON mi.movement_id = m.id
             WHERE mi.item_id = items.id AND m.type = 'IN'
             ORDER BY m.date DESC LIMIT 1) as last_price,
            (SELECT m.date FROM movement_items mi
             JOIN movements m ON mi.movement_id = m.id
             WHERE mi.item_id = items.id AND m.type = 'IN'
             ORDER BY m.date DESC LIMIT 1) as last_date
            FROM items WHERE supplier_id = %s AND is_deleted = 0
        """
        return self.db.execute_query(query, (supplier_id,))

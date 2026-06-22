from models.base_model import BaseModel

class Batch(BaseModel):
    table_name = "batches"

    def get_by_item(self, item_id, include_expired=True):
        query = "SELECT * FROM batches WHERE item_id = %s"
        if not include_expired:
            query += " AND (expiry_date IS NULL OR expiry_date >= CURRENT_DATE)"
        query += " AND quantity > 0 ORDER BY expiry_date ASC" # FIFO/Earliest expiry
        return self.db.execute_query(query, (item_id,))

    def update_quantity(self, batch_id, change):
        query = "UPDATE batches SET quantity = quantity + %s WHERE id = %s"
        self.db.execute_query(query, (change, batch_id), commit=True)

    def get_expiring_soon(self, months=6):
        query = """
            SELECT b.*, i.name as item_name, i.code as item_code
            FROM batches b
            JOIN items i ON b.item_id = i.id
            WHERE b.expiry_date <= CURRENT_DATE + ( %s  * INTERVAL '1 month')
            AND b.expiry_date >= CURRENT_DATE
            AND b.quantity > 0
        """
        return self.db.execute_query(query, (months,))

    def get_expired(self):
        query = """
            SELECT b.*, i.name as item_name, i.code as item_code
            FROM batches b
            JOIN items i ON b.item_id = i.id
            WHERE b.expiry_date < CURRENT_DATE
            AND b.quantity > 0
        """
        return self.db.execute_query(query)

from models.base_model import BaseModel

class Movement(BaseModel):
    table_name = "movements"

    def create_movement(self, movement_data, items_list):
        """
        movement_data: dict with movement headers
        items_list: list of dicts with {'item_id': id, 'quantity': q, 'price': p, 'batch_info': {...}}
        """
        movement_id = self.create(movement_data)

        from models.batch import Batch
        batch_model = Batch()

        for item in items_list:
            quantity = item['quantity']

            if movement_data['type'] == 'IN':
                # Create or Update Batch
                b_info = item.get('batch_info', {})
                batch_data = {
                    "item_id": item['item_id'],
                    "batch_number": b_info.get('batch_number', 'DEFAULT'),
                    "quantity": quantity,
                    "production_date": b_info.get('production_date'),
                    "expiry_date": b_info.get('expiry_date')
                }
                batch_id = batch_model.create(batch_data)

                # Link movement item to batch
                item_query = "INSERT INTO movement_items (movement_id, item_id, batch_id, quantity, price) VALUES ( %s ,  %s ,  %s ,  %s ,  %s )"
                self.db.execute_query(item_query, (movement_id, item['item_id'], batch_id, quantity, item.get('price', 0)), commit=True)

                # Update item total stock
                update_stock_query = "UPDATE items SET current_stock = current_stock +  %s  WHERE id =  %s "
                self.db.execute_query(update_stock_query, (quantity, item['item_id']), commit=True)

            else: # OUT
                # Deduct from batches using FIFO (Earliest expiry first)
                batches = batch_model.get_by_item(item['item_id'], include_expired=True)
                remaining_to_deduct = quantity

                for b in batches:
                    if remaining_to_deduct <= 0: break

                    deduct_qty = min(b['quantity'], remaining_to_deduct)
                    batch_model.update_quantity(b['id'], -deduct_qty)

                    # Record movement item for this batch
                    item_query = "INSERT INTO movement_items (movement_id, item_id, batch_id, quantity, price) VALUES ( %s ,  %s ,  %s ,  %s ,  %s )"
                    self.db.execute_query(item_query, (movement_id, item['item_id'], b['id'], deduct_qty, item.get('price', 0)), commit=True)

                    remaining_to_deduct -= deduct_qty

                # Update item total stock
                update_stock_query = "UPDATE items SET current_stock = current_stock -  %s  WHERE id =  %s "
                self.db.execute_query(update_stock_query, (quantity, item['item_id']), commit=True)

        return movement_id

    def get_movement_details(self, movement_id):
        query = """
            SELECT mi.*, i.name as item_name, i.code as item_code, i.unit, b.batch_number
            FROM movement_items mi
            JOIN items i ON mi.item_id = i.id
            LEFT JOIN batches b ON mi.batch_id = b.id
            WHERE mi.movement_id =  %s
        """
        return self.db.execute_query(query, (movement_id,))

    def get_history(self, type=None, start_date=None, end_date=None, limit=None, offset=None):
        query = "SELECT m.*, s.name as supplier_name FROM movements m LEFT JOIN suppliers s ON m.supplier_id = s.id WHERE 1=1"
        params = []
        if type:
            query += " AND m.type =  %s "
            params.append(type)
        if start_date:
            query += " AND m.date >=  %s "
            params.append(start_date)
        if end_date:
            query += " AND m.date <=  %s "
            params.append(end_date)
        query += " ORDER BY m.date DESC"

        if limit:
            query += " LIMIT %s"
            params.append(limit)
        if offset:
            query += " OFFSET %s"
            params.append(offset)

        return self.db.execute_query(query, tuple(params))

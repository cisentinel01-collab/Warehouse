from sqlalchemy.orm import Session
from app.models.orm_models import Movement, MovementItem, Batch, Item
from app.logging.logger import app_logger
from datetime import datetime

class StockService:
    def __init__(self, db: Session):
        self.db = db

    def record_movement(self, movement_data: dict, items_list: list) -> Movement:
        try:
            movement = Movement(**movement_data)
            self.db.add(movement)
            self.db.flush() # Get movement ID

            for item_data in items_list:
                item_id = item_data['item_id']
                qty = item_data['quantity']

                # Update Item stock
                item = self.db.query(Item).filter(Item.id == item_id).first()
                if not item: continue

                if movement.type == 'IN':
                    item.current_stock += qty
                    # Create Batch
                    batch = Batch(
                        item_id=item_id,
                        batch_number=item_data.get('batch_number', 'DEFAULT'),
                        quantity=qty,
                        production_date=item_data.get('production_date'),
                        expiry_date=item_data.get('expiry_date')
                    )
                    self.db.add(batch)
                    self.db.flush()
                    batch_id = batch.id
                else:
                    item.current_stock -= qty
                    # FIFO Deduction from batches
                    batches = self.db.query(Batch).filter(
                        Batch.item_id == item_id, Batch.quantity > 0
                    ).order_by(Batch.expiry_date.asc()).all()

                    remaining = qty
                    batch_id = None
                    for b in batches:
                        if remaining <= 0: break
                        deduct = min(b.quantity, remaining)
                        b.quantity -= deduct
                        remaining -= deduct
                        batch_id = b.id # Simplification: link to last touched batch or handle split?
                                       # ERP usually splits MovementItems.

                mi = MovementItem(
                    movement_id=movement.id,
                    item_id=item_id,
                    batch_id=batch_id,
                    quantity=qty,
                    price=item_data.get('price', 0.0)
                )
                self.db.add(mi)

            self.db.commit()
            app_logger.info(f"Movement recorded: {movement.reference_no}")
            return movement
        except Exception as e:
            self.db.rollback()
            app_logger.error(f"Movement failed: {e}")
            raise e

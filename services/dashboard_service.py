from sqlalchemy.orm import Session
from models.inventory import Item, StockLot
from datetime import datetime, timedelta
from sqlalchemy import func

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_stats(self):
        total_items = self.db.query(Item).count()
        low_stock = self.db.query(Item).filter(Item.current_stock <= Item.min_stock).count()

        # Date logic using Python datetime for DB independence
        future_date = datetime.now() + timedelta(days=180)
        expiring_soon = self.db.query(StockLot).filter(
            StockLot.expiry_date >= datetime.now().date(),
            StockLot.expiry_date <= future_date.date()
        ).count()

        return {
            "total_items": total_items,
            "low_stock": low_stock,
            "expiring_soon": expiring_soon
        }

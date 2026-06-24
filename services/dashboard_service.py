from sqlalchemy.orm import Session
from sqlalchemy import func
from models.inventory import Item, StockLot
from models.accounting import JournalEntry

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_stats(self):
        stats = {}
        stats['total_items'] = self.db.query(func.count(Item.id)).filter(Item.active == True).scalar() or 0
        stats['reorder_count'] = self.db.query(func.count(Item.id)).filter(
            Item.current_stock < Item.min_stock, Item.active == True
        ).scalar() or 0

        # Financials - Placeholder for complex ledger sum
        stats['total_value'] = 0.0
        stats['total_in'] = 0.0
        stats['total_out'] = 0.0

        stats['expired_count'] = self.db.query(func.count(StockLot.id)).filter(
            StockLot.expiry_date < func.now(), StockLot.quantity > 0
        ).scalar() or 0

        stats['expiring_count'] = self.db.query(func.count(StockLot.id)).filter(
            StockLot.expiry_date >= func.now(),
            StockLot.expiry_date <= func.text('CURRENT_DATE + INTERVAL \'6 months\''),
            StockLot.quantity > 0
        ).scalar() or 0

        # Detailed lists (empty for now, to be populated as needed)
        stats['stock_status'] = []
        stats['expiring_items'] = []
        stats['reorder_items'] = []
        stats['top_item'] = "N/A"
        stats['top_supplier'] = "N/A"

        return stats

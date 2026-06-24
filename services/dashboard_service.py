from sqlalchemy.orm import Session
from models.inventory import Item, StockLot
from datetime import datetime, timedelta
from sqlalchemy import func

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_stats(self):
        from models.inventory import Movement

        total_items = self.db.query(Item).count()
        low_stock = self.db.query(Item).filter(Item.current_stock <= Item.min_stock).count()

        # Expiring Soon (Next 6 months)
        future_date = datetime.now() + timedelta(days=180)
        expiring_soon = self.db.query(StockLot).filter(
            StockLot.expiry_date >= datetime.now().date(),
            StockLot.expiry_date <= future_date.date(),
            StockLot.quantity > 0
        ).count()

        # New: Total Inventory Value (requires price tracking)
        # For now, let's estimate or use last movement price if available
        # Implementation depends on business logic, here we'll use a placeholder or sum
        # But for "Smart Dashboard", we should provide more KPIs

        # Recent Movements (Last 7 Days)
        last_week = datetime.now() - timedelta(days=7)
        inbound = self.db.query(func.count(Movement.id)).filter(Movement.type == 'IN', Movement.date >= last_week).scalar() or 0
        outbound = self.db.query(func.count(Movement.id)).filter(Movement.type == 'OUT', Movement.date >= last_week).scalar() or 0

        # Categorized Stock
        cats = self.db.query(Item.category, func.count(Item.id)).group_by(Item.category).all()
        category_dist = {str(cat): count for cat, count in cats}

        return {
            "total_items": total_items,
            "low_stock": low_stock,
            "expiring_soon": expiring_soon,
            "inbound_7d": inbound,
            "outbound_7d": outbound,
            "category_dist": category_dist
        }

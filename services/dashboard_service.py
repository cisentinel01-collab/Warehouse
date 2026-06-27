from sqlalchemy.orm import Session
from models.inventory import Item, StockLot
from datetime import datetime, timedelta
from sqlalchemy import func, text

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_stats(self):
        from models.inventory import Movement

        # 1. Base Stats
        total_items = self.db.query(Item).count()
        low_stock = self.db.query(Item).filter(Item.current_stock <= Item.min_stock).count()

        future_date = datetime.now() + timedelta(days=180)
        expiring_soon = self.db.query(StockLot).filter(
            StockLot.expiry_date >= datetime.now().date(),
            StockLot.expiry_date <= future_date.date(),
            StockLot.quantity > 0
        ).count()

        # 2. Advanced KPIs
        # Total Valuation using subquery for speed
        total_value = self.db.execute(text("""
            SELECT SUM(i.current_stock * COALESCE(
                (SELECT price FROM movement_items mi
                 JOIN movements m ON mi.movement_id = m.id
                 WHERE mi.item_id = i.id AND m.type = 'IN'
                 ORDER BY m.date DESC LIMIT 1), 0))
            FROM items i WHERE i.current_stock > 0
        """)).scalar() or 0.0

        # Movement Trends (Last 7 Days - Daily breakdown)
        trends = []
        for i in range(6, -1, -1):
            day = (datetime.now() - timedelta(days=i)).date()
            in_qty = self.db.execute(text(
                "SELECT SUM(mi.quantity) FROM movement_items mi JOIN movements m ON mi.movement_id = m.id "
                "WHERE m.type = 'IN' AND DATE(m.date) = :d"
            ), {"d": day}).scalar() or 0
            out_qty = self.db.execute(text(
                "SELECT SUM(mi.quantity) FROM movement_items mi JOIN movements m ON mi.movement_id = m.id "
                "WHERE m.type = 'OUT' AND DATE(m.date) = :d"
            ), {"d": day}).scalar() or 0
            trends.append({"date": day.strftime("%m/%d"), "in": float(in_qty), "out": float(out_qty)})

        # 3. Beast Mode Analytics (Level 6)
        # Top Moving Items (Last 30 days - By Volume)
        last_month = datetime.now() - timedelta(days=30)
        top_items_res = self.db.execute(text("""
            SELECT i.name, SUM(mi.quantity) as total
            FROM movement_items mi
            JOIN items i ON mi.item_id = i.id
            JOIN movements m ON mi.movement_id = m.id
            WHERE m.date >= :lm AND m.type = 'OUT'
            GROUP BY i.name ORDER BY total DESC LIMIT 8
        """), {"lm": last_month}).fetchall()
        top_moving = [{"name": r[0], "value": float(r[1])} for r in top_items_res]

        # Top Supplier (Highest total purchase value)
        top_supplier_res = self.db.execute(text("""
            SELECT s.name, SUM(m.final_total) as val
            FROM movements m
            JOIN suppliers s ON m.supplier_id = s.id
            WHERE m.type = 'IN'
            GROUP BY s.name ORDER BY val DESC LIMIT 1
        """)).first()
        top_supplier = {"name": top_supplier_res[0], "value": float(top_supplier_res[1])} if top_supplier_res else {"name": "N/A", "value": 0}

        # Inventory Aging (Items not moved in 90 days)
        ninety_days_ago = datetime.now() - timedelta(days=90)
        aging_count = self.db.execute(text("""
            SELECT COUNT(*) FROM items i
            WHERE i.id NOT IN (
                SELECT DISTINCT mi.item_id FROM movement_items mi
                JOIN movements m ON mi.movement_id = m.id
                WHERE m.date >= :nd
            ) AND i.current_stock > 0
        """), {"nd": ninety_days_ago}).scalar() or 0

        # Categorized Distribution
        cats = self.db.query(Item.category, func.count(Item.id)).group_by(Item.category).all()
        category_dist = {str(cat or "Other"): count for cat, count in cats}

        # Recent Movements (Live Feed)
        recent_movements = []
        try:
            from models.inventory import Movement
            movements = self.db.query(Movement).order_by(Movement.date.desc()).limit(10).all()
            for m in movements:
                total_qty = sum(mi.quantity for mi in m.items)
                recent_movements.append({
                    'type': m.type,
                    'ref': m.reference_no,
                    'qty': total_qty,
                    'time': m.date.strftime("%H:%M:%S")
                })
        except Exception as e:
            app_logger.error(f"Live feed error: {e}")

        return {
            "total_items": total_items,
            "low_stock": low_stock,
            "expiring_soon": expiring_soon,
            "total_value": float(total_value),
            "trends": trends,
            "top_moving": top_moving,
            "top_supplier": top_supplier,
            "category_dist": category_dist,
            "aging_items": int(aging_count),
            "live_feed": recent_movements
        }

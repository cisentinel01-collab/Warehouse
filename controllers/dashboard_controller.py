from models.item import Item
from models.supplier import Supplier
from models.audit_log import AuditLog

class DashboardController:
    def __init__(self):
        self.item_model = Item()
        self.supplier_model = Supplier()
        self.audit_model = AuditLog()

    def get_dashboard_stats(self):
        from database.db_manager import DBManager
        db = DBManager()

        # KPIs using COUNT/SUM instead of fetching all records
        stats = {}

        res = db.execute_query("SELECT COUNT(*) as count, SUM(current_stock) as qty FROM items WHERE is_deleted = 0")[0]
        stats['total_items'] = res['count'] or 0
        stats['total_qty'] = res['qty'] or 0

        stats['suppliers_count'] = db.execute_query("SELECT COUNT(*) as count FROM suppliers WHERE is_deleted = 0")[0]['count'] or 0

        # Financial Stats
        stats['total_value'] = db.execute_query("SELECT SUM(i.current_stock * COALESCE((SELECT mi.price FROM movement_items mi WHERE mi.item_id = i.id ORDER BY mi.id DESC LIMIT 1), 0)) as total FROM items i WHERE i.is_deleted = 0")[0]['total'] or 0
        stats['total_in'] = db.execute_query("SELECT SUM(final_total) as total FROM movements WHERE type = 'IN'")[0]['total'] or 0
        stats['total_out'] = db.execute_query("SELECT SUM(final_total) as total FROM movements WHERE type = 'OUT'")[0]['total'] or 0

        # Performance Stats
        top_item = db.execute_query("""
            SELECT i.name, SUM(mi.quantity) as qty
            FROM movement_items mi
            JOIN items i ON mi.item_id = i.id
            JOIN movements m ON mi.movement_id = m.id
            WHERE m.type = 'OUT'
            GROUP BY i.name ORDER BY qty DESC LIMIT 1
        """)
        stats['top_item'] = top_item[0]['name'] if top_item else "N/A"

        top_supplier = db.execute_query("""
            SELECT s.name, COUNT(m.id) as count
            FROM movements m
            JOIN suppliers s ON m.supplier_id = s.id
            WHERE m.type = 'IN'
            GROUP BY s.name ORDER BY count DESC LIMIT 1
        """)
        stats['top_supplier'] = top_supplier[0]['name'] if top_supplier else "N/A"

        # Category Distribution (Optimized query)
        cat_data = db.execute_query("SELECT COALESCE(category, 'غير مصنف') as cat, SUM(current_stock) as qty FROM items WHERE is_deleted = 0 GROUP BY category")
        stats['category_data'] = {r['cat']: r['qty'] for r in cat_data}

        # Alerts & Lists
        stats['expiring_items'] = db.execute_query("""
            SELECT i.name, i.code, b.expiry_date,
            EXTRACT(YEAR FROM age(b.expiry_date, CURRENT_DATE)) * 12 + EXTRACT(MONTH FROM age(b.expiry_date, CURRENT_DATE)) as months_left
            FROM batches b
            JOIN items i ON b.item_id = i.id
            WHERE b.expiry_date <= CURRENT_DATE + INTERVAL '6 months'
            AND b.expiry_date >= CURRENT_DATE
            AND b.quantity > 0
            ORDER BY b.expiry_date ASC
            LIMIT 10
        """)
        stats['expiring_count'] = len(stats['expiring_items'])
        stats['expired_count'] = db.execute_query("SELECT COUNT(*) as count FROM batches WHERE expiry_date < CURRENT_DATE AND quantity > 0")[0]['count'] or 0

        reorder_list = db.execute_query("""
            SELECT i.name, i.current_stock, i.min_stock, s.name as supplier_name
            FROM items i
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            WHERE i.current_stock < i.min_stock AND i.is_deleted = 0
            LIMIT 10
        """)
        stats['reorder_items'] = reorder_list
        stats['reorder_count'] = len(reorder_list)

        stats['stock_status'] = self.item_model.get_low_stock()[:10]

        return stats

    def get_recent_activities(self):
        return self.audit_model.get_logs(limit=8)

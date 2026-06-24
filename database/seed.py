from models.user import User
from models.inventory import Supplier
from models.inventory import Item
from models.inventory import Location
from database.db_manager import DBManager
import bcrypt

def seed_data():
    db = DBManager()

    # 1. Users - Two Roles Only
    user_model = User()
    users = [
        {"username": "manager", "password": "123", "full_name": "مسؤول المخزن", "role": "warehouse_manager"},
        {"username": "followup", "password": "123", "full_name": "المتابعة", "role": "follow_up"}
    ]
    for u in users:
        if not db.execute_query("SELECT id FROM users WHERE username = %s", (u['username'],)):
            user_model.create_user(u)

    # 2. Locations
    loc_model = Location()
    locations = ["مخزن رئيسي", "رف A1", "رف A2"]
    for l in locations:
        if not db.execute_query("SELECT id FROM locations WHERE name = %s", (l,)):
            loc_model.create({"name": l, "description": "موقع تخزين"})

    # 3. Suppliers
    supplier_model = Supplier()
    suppliers = [
        {"name": "شركة الملاحة العربية", "phone": "0123456789", "email": "info@arabmarine.com", "address": "الإسكندرية"},
        {"name": "مورد الخليج للخدمات", "phone": "9876543210", "email": "sales@gulfserv.com", "address": "دبي"}
    ]
    for s in suppliers:
        if not db.execute_query("SELECT id FROM suppliers WHERE name = %s", (s['name'],)):
            supplier_model.create(s)

    print("Data seeding completed successfully with 2 roles.")

if __name__ == "__main__":
    seed_data()

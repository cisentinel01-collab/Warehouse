from models.user import User
from models.inventory import Supplier
from models.inventory import Item
from models.inventory import Location
from database.db_manager import DBManager
import bcrypt

from database.session import Session

def seed_data():
    db_session = Session()
    db_manager = DBManager()

    # 1. Users - Two Roles Only
    users = [
        {"username": "manager", "password": "123", "full_name": "مسؤول المخزن", "role": "warehouse_manager"},
        {"username": "followup", "password": "123", "full_name": "المتابعة", "role": "follow_up"}
    ]
    for u in users:
        if not db_manager.execute_query("SELECT id FROM users WHERE username = %s", (u['username'],)):
            password_hash = bcrypt.hashpw(u['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            new_user = User(
                username=u['username'],
                password_hash=password_hash,
                full_name=u['full_name'],
                role=u['role']
            )
            db_session.add(new_user)

    # 2. Locations
    locations = ["مخزن رئيسي", "رف A1", "رف A2"]
    for l in locations:
        if not db_manager.execute_query("SELECT id FROM locations WHERE name = %s", (l,)):
            new_loc = Location(name=l, description="موقع تخزين")
            db_session.add(new_loc)

    # 3. Suppliers
    suppliers = [
        {"name": "شركة الملاحة العربية", "phone": "0123456789", "email": "info@arabmarine.com", "address": "الإسكندرية"},
        {"name": "مورد الخليج للخدمات", "phone": "9876543210", "email": "sales@gulfserv.com", "address": "دبي"}
    ]
    for s in suppliers:
        if not db_manager.execute_query("SELECT id FROM suppliers WHERE name = %s", (s['name'],)):
            new_sup = Supplier(**s)
            db_session.add(new_sup)

    db_session.commit()
    db_session.close()

    print("Data seeding completed successfully with 2 roles.")

if __name__ == "__main__":
    seed_data()

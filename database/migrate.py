import os
from models.user import User
from database.db_manager import DBManager

def migrate():
    db = DBManager()

    # Initialize Schema if tables don't exist
    try:
        schema_path = "database/schema.sql"
        if os.path.exists(schema_path):
            print("Initializing PostgreSQL Database schema...")
            with open(schema_path, "r", encoding="utf-8") as f:
                sql = f.read()
                db.execute_query(sql, commit=True)
    except Exception as e:
        print(f"Schema initialization warning: {e}")

    user_model = User()

    # Requirements:
    # 1. Admin (Full access + User Management) - pass: adminyousef
    # 2. مسؤول المخزن (Full access except Users)
    # 3. المتابعة (View only)

    # Check if any admin exists. If not, create the default one.
    res = db.execute_query("SELECT COUNT(*) as count FROM users WHERE role = %s", ('admin',))
    if res[0]['count'] == 0:
        print("Creating default admin...")
        user_model.create_user({
            "username": "admin",
            "password": "adminyousef",
            "full_name": "المدير العام",
            "role": "admin"
        })

    # Check for warehouse_manager
    res = db.execute_query("SELECT COUNT(*) as count FROM users WHERE role = %s", ('warehouse_manager',))
    if res[0]['count'] == 0:
        print("Creating default manager...")
        user_model.create_user({
            "username": "manager",
            "password": "123",
            "full_name": "مسؤول المخزن",
            "role": "warehouse_manager"
        })

    # Check for follow_up
    res = db.execute_query("SELECT COUNT(*) as count FROM users WHERE role = %s", ('follow_up',))
    if res[0]['count'] == 0:
        print("Creating default follow-up user...")
        user_model.create_user({
            "username": "user",
            "password": "123",
            "full_name": "المتابعة",
            "role": "follow_up"
        })

    print("Migration complete. System ready.")

if __name__ == "__main__":
    migrate()

from database.db_manager import DBManager


class DeviceController:

    @staticmethod
    def get_all_devices():
        db = DBManager()

        return db.execute_query("""
            SELECT *
            FROM devices
            ORDER BY first_seen DESC
        """)

    @staticmethod
    def activate_device(device_id, expiry_date):
        db = DBManager()

        db.execute_query(
            """
            UPDATE devices
            SET status='active',
                expiry_date=%s
            WHERE id=%s
            """,
            (expiry_date, device_id),
            commit=True
        )

    @staticmethod
    def activate_for_one_year(device_id):
        db = DBManager()

        db.execute_query(
            """
            UPDATE devices
            SET status='active',
                expiry_date=CURRENT_DATE + INTERVAL '1 year'
            WHERE id=%s
            """,
            (device_id,),
            commit=True
        )

    @staticmethod
    def activate_for_one_month(device_id):
        db = DBManager()

        db.execute_query(
            """
            UPDATE devices
            SET status='active',
                expiry_date=CURRENT_DATE + INTERVAL '1 month'
            WHERE id=%s
            """,
            (device_id,),
            commit=True
        )

    @staticmethod
    def block_device(device_id):
        db = DBManager()

        db.execute_query(
            """
            UPDATE devices
            SET status='blocked'
            WHERE id=%s
            """,
            (device_id,),
            commit=True
        )

    @staticmethod
    def set_pending(device_id):
        db = DBManager()

        db.execute_query(
            """
            UPDATE devices
            SET status='pending'
            WHERE id=%s
            """,
            (device_id,),
            commit=True
        )

    @staticmethod
    def unblock_device(device_id):
        db = DBManager()

        db.execute_query(
            """
            UPDATE devices
            SET status='active'
            WHERE id=%s
            """,
            (device_id,),
            commit=True
        )

    @staticmethod
    def delete_device(device_id):
        db = DBManager()

        db.execute_query(
            """
            DELETE FROM devices
            WHERE id=%s
            """,
            (device_id,),
            commit=True
        )
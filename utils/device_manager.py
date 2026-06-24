import socket
import uuid
from database.db_manager import DBManager


def get_device_id():
    """
    إنشاء معرف فريد للجهاز
    """
    return str(uuid.getnode())


def get_computer_name():
    """
    الحصول على اسم الكمبيوتر
    """
    return socket.gethostname()


def register_device():
    """
    تسجيل الجهاز إذا لم يكن موجوداً
    """
    db = DBManager()

    device_id = get_device_id()
    computer_name = get_computer_name()

    existing = db.execute_query(
        """
        SELECT * FROM devices
        WHERE device_id = %s
        """,
        (device_id,)
    )

    if not existing:

        db.execute_query(
            """
            INSERT INTO devices(device_id, computer_name)
            VALUES (%s, %s)
            """,
            (device_id, computer_name),
            commit=True
        )

    return device_id


def check_device_status():
    """
    التحقق من حالة الجهاز
    """
    db = DBManager()

    device_id = get_device_id()

    result = db.execute_query(
        """
        SELECT status, expiry_date
        FROM devices
        WHERE device_id = %s
        """,
        (device_id,)
    )

    if not result:
        return False, "الجهاز غير مسجل"

    device = result[0]

    if device["status"] == "blocked":
        return False, "تم حظر هذا الجهاز"

    if device["status"] == "pending":
        return False, "يرجى التواصل مع المدير لتفعيل الجهاز"

    if device["expiry_date"] is not None:
        from datetime import date

        if device["expiry_date"] < date.today():
            return False, "انتهت صلاحية هذا الجهاز"

    return True, "OK"
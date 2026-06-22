from models.base_model import BaseModel
import socket

class AuditLog(BaseModel):
    table_name = "audit_logs"

    def log(self, user_id, action, table_name, record_id, details=None, old_value=None, new_value=None):
        try:
            device_name = socket.gethostname()
        except:
            device_name = "Unknown"

        data = {
            "user_id": user_id,
            "action": action,
            "table_name": table_name,
            "record_id": record_id,
            "details": details,
            "old_value": str(old_value) if old_value else None,
            "new_value": str(new_value) if new_value else None,
            "device_name": device_name
        }
        self.create(data)

    def get_logs(self, limit=100):
        query = """
            SELECT al.*, u.full_name as user_name
            FROM audit_logs al
            LEFT JOIN users u ON al.user_id = u.id
            ORDER BY al.timestamp DESC LIMIT %s
        """
        return self.db.execute_query(query, (limit,))

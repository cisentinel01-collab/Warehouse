from database.db_manager import DBManager

class BaseModel:
    table_name = ""

    def __init__(self):
        self.db = DBManager()

    def get_all(self, include_deleted=False):
        query = f"SELECT * FROM {self.table_name}"
        if not include_deleted:
            if self.table_name == 'users':
                query += " WHERE is_active = 1"
            else:
                query += " WHERE is_deleted = 0"
        return self.db.execute_query(query)

    def get_by_id(self, record_id):
        query = f"SELECT * FROM {self.table_name} WHERE id = %s"
        results = self.db.execute_query(query, (record_id,))
        return results[0] if results else None

    def create(self, data):
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders}) RETURNING id"
        return self.db.execute_query(query, tuple(data.values()), commit=True)

    def update(self, record_id, data):
        set_clause = ", ".join([f"{col} = %s" for col in data.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s"
        params = tuple(data.values()) + (record_id,)
        self.db.execute_query(query, params, commit=True)

    def soft_delete(self, record_id):
        query = f"UPDATE {self.table_name} SET is_deleted = 1 WHERE id = %s"
        self.db.execute_query(query, (record_id,), commit=True)

    def delete(self, record_id):
        query = f"DELETE FROM {self.table_name} WHERE id = %s"
        self.db.execute_query(query, (record_id,), commit=True)

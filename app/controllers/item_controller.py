from models.item import Item
from models.audit_log import AuditLog
from utils.auth import AuthManager

class ItemController:
    def __init__(self):
        self.model = Item()
        self.audit = AuditLog()

    def get_all_items(self, limit=None, offset=None):
        return self.model.get_all_with_location(limit=limit, offset=offset)

    def add_item(self, data):
        item_id = self.model.create(data)
        user = AuthManager.get_current_user()
        self.audit.log(user['id'] if user else None, "Add Item", "items", item_id, f"Code: {data['code']}")
        return item_id

    def update_item(self, item_id, data):
        old_val = self.model.get_by_id(item_id)
        self.model.update(item_id, data)
        user = AuthManager.get_current_user()
        self.audit.log(user['id'] if user else None, "Update Item", "items", item_id, old_value=old_val, new_value=data)

    def search_items(self, term):
        return self.model.search(term)

    def delete_item(self, i_id):
        self.model.update(i_id, {"is_deleted": 1})

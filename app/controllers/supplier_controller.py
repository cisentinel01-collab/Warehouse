from models.supplier import Supplier
from models.audit_log import AuditLog
from utils.auth import AuthManager

class SupplierController:
    def __init__(self):
        self.model = Supplier()
        self.audit = AuditLog()

    def get_all_suppliers(self):
        return self.model.get_all()

    def add_supplier(self, data):
        s_id = self.model.create(data)
        user = AuthManager.get_current_user()
        self.audit.log(user['id'] if user else None, "Add Supplier", "suppliers", s_id)
        return s_id

    def search_suppliers(self, term):
        return self.model.search(term)

    def update_supplier(self, s_id, data):
        self.model.update(s_id, data)
        user = AuthManager.get_current_user()
        self.audit.log(user['id'] if user else None, "Update Supplier", "suppliers", s_id)

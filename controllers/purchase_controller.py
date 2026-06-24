from sqlalchemy.orm import Session

class PurchaseController:
    def __init__(self, db: Session = None):
        self.db = db

    def get_pos(self):
        return []

    def generate_suggested_pos(self):
        return []

    def generate_po_pdf(self, po_id):
        return ""

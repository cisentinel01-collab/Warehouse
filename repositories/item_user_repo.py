from repositories.base_repository import BaseRepository
from models.inventory import Item
from models.user import User
from sqlalchemy.orm import Session

class ItemRepository(BaseRepository[Item]):
    def __init__(self, db: Session):
        super().__init__(Item, db)

    def get_by_code(self, code: str) -> Item:
        return self.db.query(Item).filter(Item.code == code).first()

    def get_by_barcode(self, barcode: str) -> Item:
        return self.db.query(Item).filter(Item.barcode == barcode).first()

    def get_by_any_identifier(self, identifier: str) -> Item:
        """Search by code or barcode."""
        return self.db.query(Item).filter(
            (Item.code == identifier) | (Item.barcode == identifier)
        ).first()

    def get_low_stock(self) -> list[Item]:
        return self.db.query(Item).filter(Item.current_stock <= Item.min_stock, Item.active == True).all()

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()

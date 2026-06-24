from repositories.base_repository import BaseRepository
from models.accounting import Account
from sqlalchemy.orm import Session

class AccountRepository(BaseRepository[Account]):
    def __init__(self, db: Session):
        super().__init__(Account, db)

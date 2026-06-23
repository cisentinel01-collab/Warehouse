import bcrypt
from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.item_user_repo import UserRepository
from app.models.orm_models import User
from app.logging.logger import app_logger

class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.db = db

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.user_repo.get_by_username(username)
        if user and self.verify_password(password, user.password_hash):
            if not user.is_active:
                app_logger.warning(f"Inactive user login attempt: {username}")
                return None
            app_logger.info(f"User authenticated: {username}")
            return user
        app_logger.warning(f"Failed login attempt: {username}")
        return None

    def create_user(self, username: str, password: str, full_name: str, role: str) -> User:
        hashed = self.hash_password(password)
        new_user = User(
            username=username,
            password_hash=hashed,
            full_name=full_name,
            role=role
        )
        return self.user_repo.create(new_user)

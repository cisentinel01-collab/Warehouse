from services.auth_service import AuthService
from sqlalchemy.orm import Session

class UserController:
    def __init__(self, db: Session):
        self.service = AuthService(db)

    def get_all_users(self):
        """Standardized method name for UserManagementView"""
        return self.service.user_repo.get_all()

    def add_user(self, data):
        return self.service.register(data)

    def delete_user(self, user_id):
        user = self.service.user_repo.get_by_id(user_id)
        if user:
            user.is_active = False
            self.service.user_repo.db.commit()
            return True
        return False

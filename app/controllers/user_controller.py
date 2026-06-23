from models.user import User

class UserController:
    def __init__(self):
        self.model = User()

    def get_all_users(self):
        return self.model.get_all()

    def add_user(self, data):
        return self.model.create_user(data)

    def update_user(self, user_id, data):
        self.model.update(user_id, data)

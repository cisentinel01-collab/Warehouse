class AuthManager:
    _current_user = None

    @classmethod
    def login(cls, username, password):
        from models.user import User
        user = User().authenticate(username, password)
        if user:
            cls._current_user = user
            return True
        return False

    @classmethod
    def get_current_user(cls):
        return cls._current_user

    @classmethod
    def logout(cls):
        cls._current_user = None

    @classmethod
    def has_permission(cls, module, action=None):
        if not cls._current_user:
            return False

        role = cls._current_user['role']

        # 1. Admin: Full Access to everything including 'users'
        if role == 'admin':
            return True

        # 2. مسئول المخزن (Full access except Users and Settings)
        if role == 'warehouse_manager':
            if module in ['users', 'settings']:
                return False
            return True

        # 3. المتابعة (Strict View Only)
        if role == 'follow_up':
            # Block any action that modifies data
            if action in ['add', 'edit', 'delete', 'submit', 'save', 'create', 'can_edit']:
                return False
            # Allow viewing core modules
            if module in ['dashboard', 'reports', 'items', 'suppliers', 'locations', 'stock_in', 'stock_out', 'purchase']:
                return True
            return False

        return False

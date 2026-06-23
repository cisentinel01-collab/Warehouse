from models.base_model import BaseModel
import bcrypt

class User(BaseModel):
    table_name = "users"

    def authenticate(self, username, password):
        query = "SELECT * FROM users WHERE username = %s AND is_active = 1"
        results = self.db.execute_query(query, (username,))

        if results:
            user = results[0]
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return user
        return None

    def create_user(self, data):
        # Hash password before storing
        password = data.pop('password')
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        data['password_hash'] = hashed.decode('utf-8')
        return self.create(data)

    def get_all_active(self):
        query = "SELECT * FROM users WHERE is_active = 1"
        return self.db.execute_query(query)

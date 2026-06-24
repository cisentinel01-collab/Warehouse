import sys
import os
sys.path.append(os.getcwd())

from database.session import Session, engine, Base
from services.auth_service import AuthService
from utils.auth import AuthManager
from models.user import User

def test_login_fix():
    print("Initializing DB...")
    Base.metadata.create_all(bind=engine)
    db = Session()
    auth_service = AuthService(db)

    try:
        # Create user with known password
        username = "auth_test"
        password = "secret_password"
        # First cleanup if exists
        old = db.query(User).filter(User.username == username).first()
        if old: db.delete(old); db.commit()

        auth_service.create_user(username, password, "Auth Tester", "admin")
        print(f"User {username} created.")

        # Test Login via AuthManager
        success = AuthManager.login(username, password)
        assert success == True
        print("AuthManager.login: SUCCESS")

        user = AuthManager.get_current_user()
        assert user['username'] == username
        print(f"Current User: {user['full_name']}")

        print("\nLogin Regression Fixed.")
    finally:
        db.close()

if __name__ == "__main__":
    test_login_fix()

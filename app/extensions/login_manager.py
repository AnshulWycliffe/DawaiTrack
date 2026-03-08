# app/extensions/login_manager.py

from flask_login import LoginManager
from app.models.user import User

login_manager = LoginManager()

login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()

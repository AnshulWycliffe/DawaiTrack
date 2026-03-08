# app/models/user.py

from datetime import datetime
from mongoengine import Document, StringField, EmailField, DateTimeField
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.config.roles import Roles


class User(UserMixin, Document):
    meta = {"collection": "users"}

    name = StringField(required=True, max_length=100)
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)

    role = StringField(
        required=True,
        default=Roles.USER,
        choices=Roles.ALL_ROLES
    )

    created_at = DateTimeField(default=datetime.utcnow)

    # ------------------------
    # Password Handling
    # ------------------------

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Flask-Login requires id as string
    def get_id(self):
        return str(self.id)
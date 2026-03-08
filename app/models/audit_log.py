
from mongoengine import *
from datetime import datetime
from datetime import date
from app.models.user import User


class AuditLog(Document):

    user = ReferenceField(User)

    action = StringField(required=True)

    entity = StringField() 
    entity_id = StringField()

    description = StringField()

    created_at = DateTimeField(default=datetime.utcnow)
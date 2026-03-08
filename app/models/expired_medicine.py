# app/models/expired_medicine.py

from datetime import datetime
from mongoengine import (
    Document,
    StringField,
    DateField,
    IntField,
    ReferenceField,
    DateTimeField
)

from app.models.user import User
from app.config.constants import EXPIRED_REQUEST_STATUS


class ExpiredMedicineRequest(Document):

    meta = {
        "collection": "expired_requests"
    }

    user = ReferenceField(User, required=True)

    medicine_name = StringField(required=True)

    expiry_date = DateField()

    quantity = IntField(required=True)

    pickup_address = StringField(required=True)

    status = StringField(
        choices=EXPIRED_REQUEST_STATUS,
        default=EXPIRED_REQUEST_STATUS[0]
    )

    created_at = DateTimeField(default=datetime.utcnow)

    disposal_method = StringField()

    disposed_by = ReferenceField(User)

    disposed_at = DateTimeField()
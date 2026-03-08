# app/models/order.py

from datetime import datetime

from mongoengine import (
    Document,
    StringField,
    FloatField,
    DateTimeField,
    ListField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    ReferenceField
)

from app.models.user import User
from app.config.constants import ORDER_STATUS , PAYMENT_METHODS


class OrderItem(EmbeddedDocument):
    name = StringField(required=True)
    price = FloatField(required=True)
    quantity = FloatField(required=True)


class Order(Document):
    meta = {"collection": "orders"}

    user = ReferenceField(User, required=True)

    items = ListField(EmbeddedDocumentField(OrderItem))

    total_amount = FloatField(required=True)

    status = StringField(default="PLACED", choices=ORDER_STATUS)

    payment_method = StringField(default="COD", choices=PAYMENT_METHODS)

    address = StringField(required=True)

    created_at = DateTimeField(default=datetime.utcnow)
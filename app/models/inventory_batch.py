# app/models/inventory_batch.py

from mongoengine import *
from datetime import datetime
from datetime import date

class InventoryBatch(Document):

    medicine = ReferenceField("Medicine", required=True)

    batch_number = StringField(required=True)

    expiry_date = DateField(required=True)

    quantity = IntField(required=True)

    purchase_price = FloatField()

    supplier = StringField()

    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "inventory_batches"
    }

    @property
    def expiry_status(self):

        days_left = (self.expiry_date - date.today()).days

        if days_left < 0:
            return "expired"

        if days_left < 90:
            return "critical"

        if days_left < 180:
            return "warning"
        else:
            return "safe"
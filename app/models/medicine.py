# app/models/medicine.py

from datetime import datetime
from mongoengine import (
    Document,
    StringField,
    FloatField,
    IntField,
    BooleanField,
    URLField,
    DateTimeField,
    ReferenceField,
    ListField,
    EmbeddedDocument,
    EmbeddedDocumentField
)

from app.models.user import User
from app.models.inventory_batch import InventoryBatch

from app.config.constants import MEDICINE_CATEGORIES

# -----------------------------
# Embedded Sub-Documents
# -----------------------------


class Pricing(EmbeddedDocument):
    mrp = FloatField(required=True)
    selling_price = FloatField(required=True)


# -----------------------------
# Main Medicine Model
# -----------------------------

class Medicine(Document):
    meta = {
        "collection": "medicines",
        "indexes": ["name", "category", "is_active"]
    }

    # Basic Info
    name = StringField(required=True, max_length=200)
    slug = StringField(required=True, unique=True)
    description = StringField()
    category = StringField(required=True, choices=MEDICINE_CATEGORIES)

    manufacturer = StringField(required=True)
    requires_prescription = BooleanField(default=False)

    # Pricing
    pricing = EmbeddedDocumentField(Pricing, required=True)

    # -----------------------------
    # Media
    # -----------------------------

    image_url = StringField(required=False)
    gallery_images = ListField(StringField())


    # Pharmacy Owner
    created_by = ReferenceField(User)

    # Status
    is_active = BooleanField(default=True)

    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    # -----------------------------
    # Business Logic Methods
    # -----------------------------

    @property
    def batches(self):
        return InventoryBatch.objects(medicine=self)

    @property
    def total_stock(self):
        return sum(batch.quantity for batch in self.batches)
    
    def is_in_stock(self):
        return self.total_stock > 0

    @property
    def available_batches(self):
        return self.batches.filter(quantity__gt=0).order_by("expiry_date")

    def calculate_discount(self):
        mrp = self.pricing.mrp
        price = self.pricing.selling_price

        if mrp and mrp > price:
            return round(((mrp - price) / mrp) * 100)

        return 0

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super(Medicine, self).save(*args, **kwargs)
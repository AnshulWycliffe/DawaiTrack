#app/services/inventory_service.py

from app.models.inventory_batch import InventoryBatch


def check_stock(medicine, quantity):

    total = sum(
        batch.quantity
        for batch in InventoryBatch.objects(
            medicine=medicine,
            quantity__gt=0
        )
    )

    return total >= quantity

def deduct_stock(medicine, quantity):

    batches = medicine.available_batches

    remaining = quantity

    for batch in batches:

        if batch.quantity >= remaining:

            batch.quantity -= remaining
            batch.save()
            return True

        else:

            remaining -= batch.quantity
            batch.quantity = 0
            batch.save()

    # Not enough stock
    if remaining > 0:
        raise Exception("Insufficient stock")
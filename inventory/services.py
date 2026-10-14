from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F

from alerts.models import Alert
from .models import InventoryItem, InventoryLog


def stock_status(quantity, threshold):
    if quantity == 0:
        return "Out of Stock"
    if quantity <= threshold:
        return "Low Stock"
    return "In Stock"


@transaction.atomic
def apply_quantity_change(*, item_id, user, change, action_type):
    """Change an item's quantity by `change` (positive or negative).

    Everything below succeeds together or not at all: the quantity update,
    the audit log row and any alert.
    """
    if change == 0:
        raise ValidationError("Quantity change cannot be zero.")

    item = InventoryItem.objects.select_for_update().get(pk=item_id)
    old_status = stock_status(item.quantity, item.threshold)

    # Guarded update: only succeeds if the result stays >= 0, even if two
    # people update the same item at the same moment.
    updated = (
        InventoryItem.objects
        .filter(pk=item.pk, quantity__gte=-change)
        .update(quantity=F("quantity") + change)
    )
    if not updated:
        raise ValidationError(
            f"Not enough stock: only {item.quantity} of {item.name} available."
        )

    item.refresh_from_db()
    new_status = stock_status(item.quantity, item.threshold)

    # Only needed if the coworker stores StockStatus as a real column
    if any(f.name == "stock_status" for f in item._meta.get_fields()):
        InventoryItem.objects.filter(pk=item.pk).update(stock_status=new_status)

    InventoryLog.objects.create(
        item=item,
        user=user,
        action_type=action_type,
        quantity_changed=change,
    )

    # Alert only when the status gets worse, so repeated updates don't spam
    if new_status != old_status and new_status != "In Stock":
        Alert.objects.create(
            item=item,
            alert_type=new_status,
            message=f"{item.name} is {new_status.lower()} "
                    f"({item.quantity} left, threshold {item.threshold}).",
        )

    return item
from django.db.models import F

from .models import InventoryItem

OUT_OF_STOCK = "Out of Stock"
LOW_STOCK = "Low Stock"
IN_STOCK = "In Stock"


def stock_status(quantity, threshold):
    """Python version of the rule, used for labels and alerts."""
    if quantity == 0:
        return OUT_OF_STOCK
    if quantity <= threshold:
        return LOW_STOCK
    return IN_STOCK


def out_of_stock_items():
    return InventoryItem.objects.filter(quantity=0)


def low_stock_items():
    """Running low but not empty: 0 < quantity <= threshold."""
    return InventoryItem.objects.filter(quantity__gt=0, quantity__lte=F("threshold"))


def items_needing_restock():
    """Low stock plus out of stock: quantity <= threshold."""
    return InventoryItem.objects.filter(quantity__lte=F("threshold"))
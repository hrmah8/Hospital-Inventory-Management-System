from django.db.models import F
from .models import InventoryItem

def get_stock_alerts():
    return (
        InventoryItem.objects
        .select_related
        .filter(quantity__lte=F("threshold"))
        .order_by("quantity","name")
    )
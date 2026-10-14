from django.db.models import F, Sum

from inventory.models import InventoryItem, InventoryLog


def stock_summary():
    items = InventoryItem.objects
    return {
        "total_items": items.count(),
        "total_units": items.aggregate(total=Sum("quantity"))["total"] or 0,
        "out_of_stock": items.filter(quantity=0).count(),
        "low_stock": items.filter(quantity__gt=0, quantity__lte=F("threshold")).count(),
    }


def recent_movements(limit=20):
    return (
        InventoryLog.objects
        .select_related("item", "user")
        .order_by("-timestamp")[:limit]
    )
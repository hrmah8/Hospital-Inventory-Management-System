from django.db.models import F, Sum

from inventory.models import InventoryItem, InventoryLog
from inventory.queries import (
    items_needing_restock,
    low_stock_items,
    out_of_stock_items,
    stock_status,
)


def stock_summary():
    return {
        "total_items": InventoryItem.objects.count(),
        "total_units": InventoryItem.objects.aggregate(total=Sum("quantity"))["total"] or 0,
        "out_of_stock": out_of_stock_items().count(),
        "low_stock": low_stock_items().count(),
    }


def low_stock_report():
    """Rows for the Low-Stock Report, biggest shortfall first."""
    items = (
        items_needing_restock()
        .select_related("category")
        .annotate(shortage=F("threshold") - F("quantity"))
        .order_by("-shortage", "name")
    )
    return [
        {
            "item": item,
            "status": stock_status(item.quantity, item.threshold),
            "shortage": item.shortage,
        }
        for item in items
    ]


def recent_movements(limit=20):
    return (
        InventoryLog.objects
        .select_related("item", "user")
        .order_by("-timestamp")[:limit]
    )
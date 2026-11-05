from django.db.models import Count, F, Sum

from inventory.models import InventoryItem, InventoryLog
from inventory.queries import (
    LOW_STOCK,
    OUT_OF_STOCK,
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


def current_inventory_report(category=None, location=""):
    """Data for the Current Inventory Report (Report1), optionally filtered."""
    items = InventoryItem.objects.all()
    if category:
        items = items.filter(category=category)
    if location:
        items = items.filter(location=location)

    rows = [
        {"item": item, "status": stock_status(item.quantity, item.threshold)}
        for item in items.select_related("category").order_by("category__name", "name")
    ]

    # order_by() clears any sorting first; otherwise the grouping would split by item name
    by_category = list(
        items.order_by()
        .values("category__name")
        .annotate(item_count=Count("pk"), total_units=Sum("quantity"))
        .order_by("category__name")
    )

    summary = {
        "total_items": len(rows),
        "total_units": sum(row["item"].quantity for row in rows),
        "low_stock": sum(1 for row in rows if row["status"] == LOW_STOCK),
        "out_of_stock": sum(1 for row in rows if row["status"] == OUT_OF_STOCK),
    }
    return {"rows": rows, "by_category": by_category, "summary": summary}


def recent_movements(limit=20):
    return (
        InventoryLog.objects
        .select_related("item", "user")
        .order_by("-timestamp")[:limit]
    )
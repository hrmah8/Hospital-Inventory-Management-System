from django.db import transaction

from inventory.queries import items_needing_restock, stock_status

from .models import Alert


@transaction.atomic
def sync_low_stock_alerts():
    """Create an alert for every low or out-of-stock item that has none of that type yet.

    Safety net for items that became low without going through the DF1 update
    flow (newly added items, edited thresholds, imported data). Safe to run
    repeatedly. Returns the number of alerts created.
    """
    created = 0
    for item in items_needing_restock():
        status = stock_status(item.quantity, item.threshold)
        if Alert.objects.filter(item=item, alert_type=status).exists():
            continue
        Alert.objects.create(
            item=item,
            alert_type=status,
            message=f"{item.name} is {status.lower()} "
                    f"({item.quantity} left, threshold {item.threshold}).",
        )
        created += 1
    return created

from django.core.management.base import BaseCommand

from alerts.services import sync_low_stock_alerts


class Command(BaseCommand):
    help = "Create alerts for low-stock and out-of-stock items that have none yet."

    def handle(self, *args, **options):
        created = sync_low_stock_alerts()
        self.stdout.write(self.style.SUCCESS(f"{created} new alert(s) created."))
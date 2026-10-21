from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from alerts.models import Alert
from alerts.services import sync_low_stock_alerts
from inventory.models import Category, InventoryItem
from inventory.queries import (
    IN_STOCK,
    items_needing_restock,
    low_stock_items,
    out_of_stock_items,
    stock_status,
)

from .services import low_stock_report, stock_summary


class LowStockAccuracyTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_user("reporter", password="pass12345")
        self.client.login(username="reporter", password="pass12345")
        category = Category.objects.create(name="Supplies")

        def make(name, quantity, threshold):
            return InventoryItem.objects.create(
                name=name, category=category, quantity=quantity,
                threshold=threshold, location="Storage A",
            )

        self.out = make("Out", 0, 5)
        self.below = make("Below", 3, 5)
        self.at_threshold = make("AtThreshold", 5, 5)
        self.just_above = make("JustAbove", 6, 5)
        self.plenty = make("Plenty", 40, 5)
        self.empty_zero_threshold = make("ZeroThresholdEmpty", 0, 0)

    def names(self, queryset):
        return {item.name for item in queryset}

    def test_low_stock_boundaries(self):
        self.assertEqual(self.names(low_stock_items()), {"Below", "AtThreshold"})

    def test_out_of_stock(self):
        self.assertEqual(self.names(out_of_stock_items()), {"Out", "ZeroThresholdEmpty"})

    def test_needing_restock_is_low_plus_out(self):
        combined = self.names(low_stock_items()) | self.names(out_of_stock_items())
        self.assertEqual(self.names(items_needing_restock()), combined)

    def test_orm_rule_matches_python_rule_for_every_item(self):
        expected = {
            i.pk for i in InventoryItem.objects.all()
            if stock_status(i.quantity, i.threshold) != IN_STOCK
        }
        actual = set(items_needing_restock().values_list("pk", flat=True))
        self.assertEqual(actual, expected)

    def test_report_rows_are_ordered_and_labelled(self):
        rows = low_stock_report()
        self.assertEqual(
            [r["item"].name for r in rows],
            ["Out", "Below", "AtThreshold", "ZeroThresholdEmpty"],
        )
        statuses = {r["item"].name: r["status"] for r in rows}
        self.assertEqual(statuses["Out"], "Out of Stock")
        self.assertEqual(statuses["Below"], "Low Stock")

    def test_summary_counts(self):
        summary = stock_summary()
        self.assertEqual(summary["low_stock"], 2)
        self.assertEqual(summary["out_of_stock"], 2)
        self.assertEqual(summary["total_items"], 6)

    def test_sync_creates_alerts_once(self):
        self.assertEqual(sync_low_stock_alerts(), 4)
        self.assertEqual(sync_low_stock_alerts(), 0)
        self.assertEqual(Alert.objects.count(), 4)

    def test_sync_ignores_healthy_items(self):
        sync_low_stock_alerts()
        healthy = Alert.objects.filter(item__in=[self.just_above, self.plenty])
        self.assertEqual(healthy.count(), 0)

    def test_report_page_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("reports:low_stock"))
        self.assertEqual(response.status_code, 302)

    def test_report_page_lists_only_items_needing_restock(self):
        response = self.client.get(reverse("reports:low_stock"))
        self.assertContains(response, "Below")
        self.assertNotContains(response, "Plenty")
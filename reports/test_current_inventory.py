import csv
import io

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from inventory.models import Category, InventoryItem
from inventory.services import apply_quantity_change

from .services import current_inventory_report


class CurrentInventoryReportTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("reporter1", password="pass12345")
        self.client.login(username="reporter1", password="pass12345")
        self.supplies = Category.objects.create(name="Supplies")
        self.fluids = Category.objects.create(name="Fluids")
        InventoryItem.objects.create(name="Gloves", category=self.supplies, quantity=3, threshold=5, location="Storage A")
        InventoryItem.objects.create(name="Syringes", category=self.supplies, quantity=40, threshold=10, location="Storage B")
        self.iv_bags = InventoryItem.objects.create(name="IV bags", category=self.fluids, quantity=0, threshold=5, location="Storage A")

    def names(self, report):
        return [row["item"].name for row in report["rows"]]

    def test_lists_all_items_sorted_by_category_then_name(self):
        report = current_inventory_report()
        self.assertEqual(self.names(report), ["IV bags", "Gloves", "Syringes"])

    def test_summary_totals(self):
        summary = current_inventory_report()["summary"]
        self.assertEqual(summary["total_items"], 3)
        self.assertEqual(summary["total_units"], 43)
        self.assertEqual(summary["low_stock"], 1)
        self.assertEqual(summary["out_of_stock"], 1)

    def test_totals_per_category(self):
        by_category = current_inventory_report()["by_category"]
        self.assertEqual(by_category, [
            {"category__name": "Fluids", "item_count": 1, "total_units": 0},
            {"category__name": "Supplies", "item_count": 2, "total_units": 43},
        ])

    def test_filter_by_category(self):
        report = current_inventory_report(category=self.supplies)
        self.assertEqual(self.names(report), ["Gloves", "Syringes"])

    def test_filter_by_location(self):
        report = current_inventory_report(location="Storage A")
        self.assertEqual(self.names(report), ["IV bags", "Gloves"])

    def test_report_updates_after_a_quantity_change(self):
        apply_quantity_change(
            item_id=self.iv_bags.pk, user=self.user, change=10, action_type="Restock"
        )
        summary = current_inventory_report()["summary"]
        self.assertEqual(summary["total_units"], 53)
        self.assertEqual(summary["out_of_stock"], 0)

    def test_page_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("reports:current_inventory"))
        self.assertEqual(response.status_code, 302)

    def test_page_shows_items(self):
        response = self.client.get(reverse("reports:current_inventory"))
        self.assertContains(response, "Gloves")
        self.assertContains(response, "Syringes")

    def test_csv_export_respects_filter(self):
        url = reverse("reports:current_inventory_export")
        response = self.client.get(url, {"category": self.supplies.pk})
        self.assertEqual(response["Content-Type"], "text/csv")
        rows = list(csv.reader(io.StringIO(response.content.decode())))
        self.assertEqual(rows[0], ["Item", "Category", "Quantity", "Threshold", "Location", "Status"])
        self.assertEqual([r[0] for r in rows[1:]], ["Gloves", "Syringes"])
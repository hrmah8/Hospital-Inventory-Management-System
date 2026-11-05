import csv
import io

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from inventory.models import Category, InventoryItem
from inventory.services import apply_quantity_change

from .services import low_stock_report


class LowStockReportTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("reporter2", password="pass12345")
        self.client.login(username="reporter2", password="pass12345")
        self.supplies = Category.objects.create(name="Supplies")
        self.fluids = Category.objects.create(name="Fluids")

        def make(name, category, quantity, threshold, location):
            return InventoryItem.objects.create(
                name=name, category=category, quantity=quantity,
                threshold=threshold, location=location,
            )

        self.iv_bags = make("IV bags", self.fluids, 0, 5, "Storage A")      # out of stock
        self.gloves = make("Gloves", self.supplies, 3, 5, "Storage A")      # low
        self.syringes = make("Syringes", self.supplies, 5, 5, "Storage B")  # exactly at threshold
        self.bandages = make("Bandages", self.supplies, 40, 5, "Storage B") # healthy

    def names(self, **filters):
        return [row["item"].name for row in low_stock_report(**filters)]

    def test_default_lists_low_and_out_of_stock(self):
        self.assertEqual(self.names(), ["IV bags", "Gloves", "Syringes"])

    def test_status_low_only(self):
        self.assertEqual(self.names(status="low"), ["Gloves", "Syringes"])

    def test_status_out_only(self):
        self.assertEqual(self.names(status="out"), ["IV bags"])

    def test_category_filter(self):
        self.assertEqual(self.names(category=self.fluids), ["IV bags"])

    def test_location_filter(self):
        self.assertEqual(self.names(location="Storage B"), ["Syringes"])

    def test_combined_filters(self):
        result = self.names(category=self.supplies, location="Storage A", status="low")
        self.assertEqual(result, ["Gloves"])

    def test_report_updates_after_a_restock(self):
        apply_quantity_change(
            item_id=self.gloves.pk, user=self.user, change=10, action_type="Restock"
        )
        self.assertNotIn("Gloves", self.names())

    def test_page_applies_filters(self):
        response = self.client.get(reverse("reports:low_stock"), {"status": "out"})
        self.assertContains(response, "IV bags")
        self.assertNotContains(response, "Gloves")

    def test_invalid_filter_shows_notice(self):
        response = self.client.get(reverse("reports:low_stock"), {"status": "bogus"})
        self.assertContains(response, "not valid")

    def test_csv_export_matches_filter(self):
        response = self.client.get(reverse("reports:low_stock_export"), {"status": "low"})
        self.assertEqual(response["Content-Type"], "text/csv")
        rows = list(csv.reader(io.StringIO(response.content.decode())))
        self.assertEqual(
            rows[0],
            ["Item", "Category", "Quantity", "Threshold", "Shortage", "Location", "Status"],
        )
        self.assertEqual([r[0] for r in rows[1:]], ["Gloves", "Syringes"])

    def test_export_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("reports:low_stock_export"))
        self.assertEqual(response.status_code, 302)
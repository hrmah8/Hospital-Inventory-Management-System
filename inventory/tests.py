from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from alerts.models import Alert
from reports.services import stock_summary

from .models import Category, InventoryItem, InventoryLog
from .services import apply_quantity_change


class InventoryFilterTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_user("tester", password="pass12345")
        self.client.login(username="tester", password="pass12345")
        supplies = Category.objects.create(name="Supplies")
        fluids = Category.objects.create(name="Fluids")
        InventoryItem.objects.create(name="Gloves", category=supplies, quantity=3, threshold=5, location="Storage A")
        InventoryItem.objects.create(name="Syringes", category=supplies, quantity=40, threshold=10,
                                     location="Storage B")
        InventoryItem.objects.create(name="IV bags", category=fluids, quantity=0, threshold=5, location="Storage A")

    def names(self, **params):
        response = self.client.get(reverse("inventory:list"), params)
        return [i.name for i in response.context["page_obj"]]

    def test_search(self):
        self.assertEqual(self.names(q="glove"), ["Gloves"])

    def test_status_low(self):
        self.assertEqual(self.names(status="low"), ["Gloves"])

    def test_status_out(self):
        self.assertEqual(self.names(status="out"), ["IV bags"])

    def test_location(self):
        self.assertEqual(sorted(self.names(location="Storage A")), ["Gloves", "IV bags"])


class QuantityUpdateTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("tester2", password="pass12345")
        self.client.login(username="tester2", password="pass12345")
        category = Category.objects.create(name="Supplies")
        self.item = InventoryItem.objects.create(
            name="Gloves", category=category, quantity=10, threshold=5, location="Storage A"
        )

    def change(self, amount, action="Restock"):
        return apply_quantity_change(
            item_id=self.item.pk, user=self.user, change=amount, action_type=action
        )

    def test_restock_updates_quantity_and_writes_log(self):
        self.change(5)
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 15)
        self.assertEqual(InventoryLog.objects.get().quantity_changed, 5)

    def test_cannot_go_below_zero(self):
        with self.assertRaises(ValidationError):
            self.change(-11, "Usage")
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 10)
        self.assertEqual(InventoryLog.objects.count(), 0)

    def test_zero_change_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.change(0)

    def test_low_stock_alert_is_created_only_once(self):
        self.change(-6, "Usage")   # 4 left, at or below threshold 5
        self.change(-1, "Usage")   # still low, no second alert
        self.assertEqual(Alert.objects.count(), 1)

    def test_report_reflects_update(self):
        before = stock_summary()
        self.change(-10, "Usage")  # now out of stock
        after = stock_summary()
        self.assertEqual(after["out_of_stock"], before["out_of_stock"] + 1)
        self.assertEqual(after["total_units"], before["total_units"] - 10)

    def test_view_updates_quantity(self):
        url = reverse("inventory:update_quantity", args=[self.item.pk])
        self.client.post(url, {"action_type": "Usage", "amount": 3})
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 7)

    def test_view_rejects_invalid_amount(self):
        url = reverse("inventory:update_quantity", args=[self.item.pk])
        self.client.post(url, {"action_type": "Usage", "amount": 0})
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 10)

    def test_view_rejects_get(self):
        url = reverse("inventory:update_quantity", args=[self.item.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
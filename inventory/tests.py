from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, InventoryItem


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



from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="items")
    quantity = models.IntegerField(default=0)
    threshold = models.IntegerField(default=5)
    location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

    @property
    def stock_status(self):
        if self.quantity == 0:
            return "Out of Stock"
        elif self.quantity <= self.threshold:
            return "Low Stock"
        return "In Stock"

class InventoryLog(models.Model):
    ACTION_CHOICES = [
        ('add', 'Add'),
        ('remove', 'Remove'),
        ('adjust', 'Adjust'),
        ('transfer', 'Transfer'),
        ('other', 'Other')
    ]

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inventory_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity_changed = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp}: {self.user} {self.action} {self.quantity_changed} {self.item}"

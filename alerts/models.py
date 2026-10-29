from django.db import models

# Create your models here.
from inventory.models import InventoryItem

class StockAlert(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('resolved', 'Resolved'),
    ]

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='alerts')
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Alert for {self.item.name} - Status: {self.status}"
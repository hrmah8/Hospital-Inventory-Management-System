from django.db import models

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

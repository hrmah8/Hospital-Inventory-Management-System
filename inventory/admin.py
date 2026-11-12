
from django.contrib import admin
from .models import Category, InventoryItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "quantity",
        "low_stock_threshold",
        "location",
        "is_low_stock",
        "updated_at",
    )

    list_filter = ("category", "location")

    search_fields = (
        "name",
        "category__name",
        "location",
    )

    ordering = ("name",)

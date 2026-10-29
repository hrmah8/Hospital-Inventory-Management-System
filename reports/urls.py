from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("low-stock/", views.low_stock_report_view, name="low_stock"),
    path("current-inventory/", views.current_inventory_report_view, name="current_inventory"),
    path("current-inventory/export/", views.current_inventory_export, name="current_inventory_export"),
]